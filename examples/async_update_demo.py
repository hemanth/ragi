"""Quick demo: Async updates with LanceDB (simplified)."""

import os
import tempfile
import time
import threading
from piragi import Ragi
from ragi.async_updater import AsyncUpdater


def main():
    """Simple async update demonstration."""
    print("Async Auto-Update Demo")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = os.path.join(tmpdir, "test.md")

        # Create initial document
        with open(doc_path, "w") as f:
            f.write("Version 1.0")

        # Load into Ragi
        print("\n1. Loading document...")
        kb = Ragi(
            doc_path,
            persist_dir=os.path.join(tmpdir, ".ragi"),
            config={"embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}},
        )
        print(f"   Loaded {kb.count()} chunks")

        # Create updater
        print("\n2. Setting up async updater...")
        updater = AsyncUpdater(
            refresh_callback=kb.refresh,
            check_interval=2.0,  # Check every 2 seconds
            max_workers=1,
        )

        # Register source
        with open(doc_path, "r") as f:
            updater.register_source(doc_path, f.read(), check_interval=2.0)

        # Start background worker
        print("3. Starting background worker...")
        updater.start()
        time.sleep(0.5)

        # Update document
        print("\n4. Updating document...")
        with open(doc_path, "w") as f:
            f.write("Version 2.0 (UPDATED!)")

        # Queries continue uninterrupted
        print("\n5. Querying (updates happen in background)...")
        for i in range(5):
            time.sleep(1)
            stats = updater.get_stats()
            print(f"   [{i+1}s] Checks: {stats['checks_performed']}, Updates: {stats['updates_performed']}")

        # Final stats
        print("\n6. Final statistics:")
        final_stats = updater.get_stats()
        for key, value in final_stats.items():
            print(f"   {key}: {value}")

        # Cleanup
        updater.stop()
        print("\n✅ Demo complete!")
        print("\nKey benefits:")
        print("  - Queries never blocked by update checks")
        print("  - Background workers handle updates")
        print("  - Configurable check intervals")
        print("  - Thread-safe LanceDB access")


if __name__ == "__main__":
    main()
