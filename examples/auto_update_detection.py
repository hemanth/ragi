"""Example: Automatic change detection for low-latency updates."""

import os
import tempfile
import time
from piragi import Ragi
from ragi.change_detection import ChangeDetector


def example_file_change_detection():
    """Demonstrate file change detection with minimal latency."""
    print("=" * 60)
    print("File Change Detection (Lazy Strategy)")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = os.path.join(tmpdir, "config.md")

        # Create initial document
        print("\n1. Creating initial document...")
        with open(doc_path, "w") as f:
            f.write("# Config v1.0\nDatabase: PostgreSQL\nCache: Redis")

        # Load into Ragi
        kb = Ragi(
            doc_path,
            persist_dir=os.path.join(tmpdir, ".ragi"),
            config={"embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}},
        )

        # Store metadata for change detection
        with open(doc_path, "r") as f:
            content = f.read()

        metadata = ChangeDetector.get_file_metadata(doc_path, content)
        print(f"   Stored metadata:")
        print(f"   - mtime: {metadata['mtime']}")
        print(f"   - hash: {metadata['content_hash'][:16]}...")

        # Simulate no change (touch file without modifying)
        print("\n2. Touching file without content change...")
        time.sleep(0.1)
        os.utime(doc_path, None)  # Update mtime

        # Check for changes (fast - uses mtime + hash)
        start = time.time()
        changed = ChangeDetector.check_file_changed(
            doc_path, metadata["mtime"], metadata["content_hash"]
        )
        elapsed = (time.time() - start) * 1000
        print(f"   Changed: {changed}")
        print(f"   ⚡ Check took: {elapsed:.2f}ms (fast path: hash comparison)")

        # Simulate actual content change
        print("\n3. Actually changing file content...")
        time.sleep(0.1)
        with open(doc_path, "w") as f:
            f.write("# Config v2.0\nDatabase: PostgreSQL\nCache: Redis\nQueue: RabbitMQ")

        # Check for changes
        start = time.time()
        changed = ChangeDetector.check_file_changed(
            doc_path, metadata["mtime"], metadata["content_hash"]
        )
        elapsed = (time.time() - start) * 1000
        print(f"   Changed: {changed}")
        print(f"   ⚡ Check took: {elapsed:.2f}ms")

        if changed:
            print(f"   → Refreshing document...")
            kb.refresh(doc_path)
            print(f"   ✓ Updated to latest version")


def example_url_change_detection():
    """Demonstrate URL change detection with HTTP conditional requests."""
    print("\n" + "=" * 60)
    print("URL Change Detection (HTTP Headers)")
    print("=" * 60)

    # Example URL (using a stable API)
    url = "https://httpbin.org/etag/test-etag-123"

    print(f"\n1. Checking URL: {url}")
    print("   Using HTTP HEAD with conditional requests...")

    # First check - no stored headers
    start = time.time()
    result = ChangeDetector.check_url_changed(url, None, None, timeout=5)
    elapsed = (time.time() - start) * 1000

    print(f"   ⚡ Check took: {elapsed:.0f}ms")
    print(f"   Changed: {result.get('changed')}")
    print(f"   ETag: {result.get('etag')}")

    # Second check - with stored ETag (should get 304 Not Modified)
    if result.get("etag"):
        print("\n2. Checking again with stored ETag...")
        start = time.time()
        result2 = ChangeDetector.check_url_changed(
            url, result.get("etag"), result.get("last_modified"), timeout=5
        )
        elapsed = (time.time() - start) * 1000

        print(f"   ⚡ Check took: {elapsed:.0f}ms")
        print(f"   Changed: {result2.get('changed')}")
        print(
            f"   Status: {'304 Not Modified' if not result2.get('changed') else '200 OK'}"
        )


def example_smart_update_workflow():
    """Demonstrate smart update workflow with check intervals."""
    print("\n" + "=" * 60)
    print("Smart Update Workflow (Check Intervals)")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = os.path.join(tmpdir, "data.md")

        # Create document
        with open(doc_path, "w") as f:
            f.write("# Data v1\nRecords: 1000")

        # Load into Ragi
        kb = Ragi(
            doc_path,
            persist_dir=os.path.join(tmpdir, ".ragi"),
            config={"embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}},
        )

        # Store metadata
        with open(doc_path, "r") as f:
            content = f.read()
        metadata = ChangeDetector.get_file_metadata(doc_path, content)

        # Custom check interval (e.g., 10 seconds for demo)
        check_interval = 2.0  # 2 seconds
        metadata["check_interval"] = check_interval

        print(f"\n1. Loaded document with check interval: {check_interval}s")

        # Immediate query - no check needed yet
        print("\n2. Query immediately (within check interval)...")
        should_check = ChangeDetector.should_check_now(
            metadata["last_checked"], check_interval
        )
        print(f"   Should check for updates: {should_check}")
        print(f"   → Skipping check, using cached version")

        # Wait and query again
        print(f"\n3. Waiting {check_interval}s...")
        time.sleep(check_interval + 0.1)

        should_check = ChangeDetector.should_check_now(
            metadata["last_checked"], check_interval
        )
        print(f"   Should check for updates: {should_check}")

        if should_check:
            print(f"   → Checking for changes...")
            changed = ChangeDetector.check_file_changed(
                doc_path, metadata["mtime"], metadata["content_hash"]
            )
            print(f"   Changed: {changed}")

            if changed:
                kb.refresh(doc_path)
                # Update metadata
                with open(doc_path, "r") as f:
                    content = f.read()
                metadata = ChangeDetector.get_file_metadata(doc_path, content)

        print(
            f"""
Latency Analysis:
─────────────────────────────────────────────────────────
Query Pattern              | Latency Impact
─────────────────────────────────────────────────────────
Within check interval      | 0ms (no check)
After interval (file)      | ~1-5ms (mtime + hash)
After interval (URL/HEAD)  | ~50-200ms (network)
After interval (URL/304)   | ~30-100ms (cached)
─────────────────────────────────────────────────────────

Recommended Intervals:
- Local files: 60s (fast checks)
- URLs (stable): 300s (5 min)
- URLs (dynamic): 60-180s
"""
        )


def main():
    """Run all change detection examples."""
    example_file_change_detection()

    try:
        example_url_change_detection()
    except Exception as e:
        print(f"\n⚠️  URL check skipped: {e}")
        print("   (Network required for URL examples)")

    example_smart_update_workflow()

    print("\n" + "=" * 60)
    print("Summary: Low-Latency Update Strategies")
    print("=" * 60)
    print(
        """
1. **Lazy Checking (Recommended)**
   - Check only when query happens
   - Skip if within check interval
   - Near-zero latency impact on queries

2. **File Detection**
   - O(1) mtime check first
   - O(n) hash check if needed
   - Total: 1-5ms for most files

3. **URL Detection**
   - HTTP HEAD with If-None-Match/If-Modified-Since
   - Server returns 304 if unchanged (no body transfer)
   - ~30-200ms depending on network

4. **Check Intervals**
   - Configure per-source or global
   - Balance freshness vs latency
   - Files: 60s+, URLs: 300s+

Usage Pattern:
```python
from piragi import Ragi
from ragi.change_detection import ChangeDetector

# Track sources with metadata
sources_metadata = {}

def smart_query(kb, query, sources):
    # Check for updates before querying
    for source in sources:
        meta = sources_metadata.get(source)
        if meta and ChangeDetector.should_check_now(
            meta['last_checked'], meta['check_interval']
        ):
            if ChangeDetector.is_url(source):
                result = ChangeDetector.check_url_changed(
                    source, meta.get('etag'), meta.get('last_modified')
                )
            else:
                result = {'changed': ChangeDetector.check_file_changed(
                    source, meta.get('mtime'), meta['content_hash']
                )}

            if result.get('changed'):
                kb.refresh(source)
                # Update metadata...

    return kb.ask(query)
```
"""
    )


if __name__ == "__main__":
    main()
