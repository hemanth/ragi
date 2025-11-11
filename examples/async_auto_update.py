"""Example: Async auto-update with background workers."""

import os
import tempfile
import time
import logging
from piragi import Ragi
from ragi.async_updater import AsyncUpdater

# Enable logging to see update activity
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(threadName)s] %(message)s"
)


def example_async_background_updates():
    """Demonstrate async background updates without blocking queries."""
    print("=" * 60)
    print("Async Background Updates (Non-Blocking)")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test documents
        doc1 = os.path.join(tmpdir, "prices.md")
        doc2 = os.path.join(tmpdir, "inventory.md")

        with open(doc1, "w") as f:
            f.write("# Prices\n\nProduct A: $100\nProduct B: $200")

        with open(doc2, "w") as f:
            f.write("# Inventory\n\nProduct A: 50 units\nProduct B: 30 units")

        # Initialize Ragi
        kb = Ragi(
            [doc1, doc2],
            persist_dir=os.path.join(tmpdir, ".ragi"),
            config={"embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}},
        )

        print(f"\n1. Loaded {kb.count()} chunks")

        # Setup async updater
        updater = AsyncUpdater(
            refresh_callback=kb.refresh,
            check_interval=5.0,  # Check every 5 seconds
            max_workers=2,
        )

        # Register sources
        print("\n2. Registering sources for auto-update...")
        with open(doc1, "r") as f:
            updater.register_source(doc1, f.read(), check_interval=3.0)
        with open(doc2, "r") as f:
            updater.register_source(doc2, f.read(), check_interval=5.0)

        # Start background workers
        print("3. Starting background workers...\n")
        updater.start()

        # Query while background updates happen
        print("4. Querying knowledge base (updates happen in background)...")
        answer = kb.ask("What is the price of Product A?")
        print(f"   Q: What is the price of Product A?")
        print(f"   A: {answer.text[:100]}...\n")

        # Simulate document update
        print("5. Updating document (in 2 seconds)...")
        time.sleep(2)
        with open(doc1, "w") as f:
            f.write("# Prices\n\nProduct A: $120 (UPDATED!)\nProduct B: $220")
        print(f"   ✓ Updated {doc1}\n")

        # Continue querying - updates happen automatically in background
        print("6. Continue querying (background worker will detect change)...")

        for i in range(6):
            time.sleep(1)
            # Query is NOT blocked by update checks
            start = time.time()
            answer = kb.ask("What is the price of Product A?")
            query_time = (time.time() - start) * 1000

            print(
                f"   [{i+1}] Query latency: {query_time:.0f}ms | Answer: {answer.text[:60]}..."
            )

        # Show stats
        print("\n7. Update statistics:")
        stats = updater.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")

        # Stop updater
        print("\n8. Stopping background workers...")
        updater.stop()


def example_manual_queue():
    """Demonstrate manually queuing updates."""
    print("\n" + "=" * 60)
    print("Manual Update Queue")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = os.path.join(tmpdir, "config.md")

        with open(doc_path, "w") as f:
            f.write("# Config v1")

        kb = Ragi(
            doc_path,
            persist_dir=os.path.join(tmpdir, ".ragi"),
            config={"embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}},
        )

        # Setup updater (but don't start scheduler)
        updater = AsyncUpdater(
            refresh_callback=kb.refresh,
            check_interval=999999,  # Effectively disable auto-checks
            max_workers=1,
        )

        with open(doc_path, "r") as f:
            updater.register_source(doc_path, f.read())

        updater.start()

        print("\n1. Manual update workflow:")
        print("   - User edits document")
        print("   - App queues update check")
        print("   - Background worker processes it")
        print("   - Queries continue uninterrupted\n")

        # Simulate user edit
        print("2. User edits document...")
        with open(doc_path, "w") as f:
            f.write("# Config v2 (UPDATED)")

        # Manually queue update
        print("3. Queuing update check (non-blocking)...")
        updater.queue_update(doc_path, priority=1)

        # Query immediately (not blocked!)
        start = time.time()
        answer = kb.ask("What version is this?")
        query_time = (time.time() - start) * 1000
        print(f"   Query completed in {query_time:.0f}ms (not blocked!)")

        # Wait for background update to complete
        print("4. Waiting for background update...")
        time.sleep(2)

        # Query again with updated content
        answer = kb.ask("What version is this?")
        print(f"   Answer: {answer.text[:80]}...")

        updater.stop()


def example_concurrent_queries_and_updates():
    """Demonstrate queries continue during updates."""
    print("\n" + "=" * 60)
    print("Concurrent Queries + Updates (No Blocking)")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple documents
        docs = []
        for i in range(5):
            doc_path = os.path.join(tmpdir, f"doc{i}.md")
            with open(doc_path, "w") as f:
                f.write(f"# Document {i}\n\nContent version 1")
            docs.append(doc_path)

        kb = Ragi(
            docs,
            persist_dir=os.path.join(tmpdir, ".ragi"),
            config={"embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}},
        )

        print(f"\n1. Loaded {len(docs)} documents, {kb.count()} chunks")

        # Setup updater
        updater = AsyncUpdater(
            refresh_callback=kb.refresh, check_interval=2.0, max_workers=3
        )

        for doc in docs:
            with open(doc, "r") as f:
                updater.register_source(doc, f.read(), check_interval=2.0)

        updater.start()

        print("2. Starting concurrent operations...\n")

        # Update documents while querying
        for i in range(5):
            # Update a document
            doc = docs[i % len(docs)]
            with open(doc, "w") as f:
                f.write(f"# Document {i % len(docs)}\n\nContent version {i+2}")

            # Query immediately (not blocked by update!)
            start = time.time()
            answer = kb.ask(f"What is in document {i % len(docs)}?")
            query_time = (time.time() - start) * 1000

            print(
                f"   [{i+1}] Updated doc{i % len(docs)}, query latency: {query_time:.0f}ms"
            )

            time.sleep(1)

        print("\n3. All queries completed without blocking!")
        print("   Background workers handled updates asynchronously")

        stats = updater.get_stats()
        print(f"\n4. Final stats:")
        print(f"   Checks: {stats['checks_performed']}")
        print(f"   Updates: {stats['updates_performed']}")
        print(f"   Queue size: {stats['queue_size']}")

        updater.stop()


def main():
    """Run all async update examples."""
    example_async_background_updates()
    example_manual_queue()
    example_concurrent_queries_and_updates()

    print("\n" + "=" * 60)
    print("Summary: Async Auto-Update Benefits")
    print("=" * 60)
    print(
        """
1. **Zero Query Latency Impact**
   - Updates happen in background threads
   - Queries never blocked
   - Consistent fast response times

2. **Flexible Update Strategies**
   - Automatic polling (time-based)
   - Manual queueing (event-driven)
   - Priority-based processing

3. **Concurrent Operations**
   - Multiple workers handle updates in parallel
   - LanceDB supports concurrent reads
   - Safe refresh operations

4. **Resource Efficient**
   - Check intervals prevent excessive polling
   - Workers sleep when idle
   - Graceful shutdown

Architecture:
┌─────────────┐
│   Queries   │ ◄──── Fast, never blocked
└─────────────┘
       │
       ▼
┌─────────────────────┐
│  LanceDB (Reads)    │ ◄──── Concurrent safe
└─────────────────────┘
       ▲
       │
┌──────────────────────┐
│  Background Workers  │ ◄──── Async updates
│  - Scheduler         │
│  - Worker 1          │
│  - Worker 2          │
└──────────────────────┘
       ▲
       │
┌──────────────────────┐
│  Change Detection    │ ◄──── Smart, fast checks
│  - File: mtime+hash  │
│  - URL: HTTP HEAD    │
└──────────────────────┘

Configuration:
```python
from piragi import Ragi
from ragi.async_updater import AsyncUpdater

kb = Ragi("./docs")

updater = AsyncUpdater(
    refresh_callback=kb.refresh,
    check_interval=300,  # 5 minutes
    max_workers=2
)

# Register sources
updater.register_source("./docs/api.md", content)
updater.start()

# Queries run uninterrupted
answer = kb.ask("question")  # Fast!

# Updates happen in background
```
"""
    )


if __name__ == "__main__":
    main()
