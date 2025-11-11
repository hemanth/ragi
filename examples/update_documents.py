"""Example: Updating documents when content changes."""

import os
import tempfile
from piragi import Ragi


def main():
    """Demonstrate document refresh capabilities."""

    # Create a temporary directory for our example
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = os.path.join(tmpdir, "product.md")

        print("=" * 60)
        print("Example: Document Update Workflow")
        print("=" * 60)

        # Initial document
        print("\n1. Creating initial document...")
        with open(doc_path, "w") as f:
            f.write(
                """# Product Documentation

## Version 1.0

### Features
- Basic authentication
- File upload
- User dashboard

### Pricing
- Free tier: 100MB storage
- Pro tier: $10/month for 1GB
"""
            )

        # Load into Ragi
        print("2. Loading into knowledge base...")
        kb = Ragi(
            doc_path,
            persist_dir=os.path.join(tmpdir, ".ragi"),
            config={"embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}},
        )
        print(f"   ✓ Loaded {kb.count()} chunks")

        # Ask a question
        print("\n3. Querying initial version...")
        answer = kb.ask("What features are available?")
        print(f"   Q: What features are available?")
        print(f"   A: {answer.text[:150]}...")

        # Update the document
        print("\n4. Updating document with new content...")
        with open(doc_path, "w") as f:
            f.write(
                """# Product Documentation

## Version 2.0

### Features
- Advanced authentication with 2FA
- File upload with previews
- User dashboard with analytics
- Real-time collaboration (NEW!)
- API access (NEW!)

### Pricing
- Free tier: 500MB storage
- Pro tier: $15/month for 5GB
- Enterprise tier: Custom pricing (NEW!)
"""
            )

        # Option 1: Full re-index (simple but inefficient)
        print("\n5. Option 1: Full re-index")
        print("   kb.clear()")
        print("   kb.add('./docs')")
        print("   → Simple but re-processes everything")

        # Option 2: Refresh specific documents (efficient!)
        print("\n6. Option 2: Refresh specific documents (RECOMMENDED)")
        chunks_before = kb.count()
        kb.refresh(doc_path)
        chunks_after = kb.count()
        print(f"   ✓ Refreshed {doc_path}")
        print(f"   ✓ Chunks: {chunks_before} → {chunks_after}")

        # Query updated content
        print("\n7. Querying updated version...")
        answer = kb.ask("What features are available?")
        print(f"   Q: What features are available?")
        print(f"   A: {answer.text[:200]}...")

        answer = kb.ask("What are the pricing tiers?")
        print(f"\n   Q: What are the pricing tiers?")
        print(f"   A: {answer.text[:200]}...")

        # Demonstrate refresh with multiple files
        print("\n" + "=" * 60)
        print("Example: Refreshing Multiple Documents")
        print("=" * 60)

        # Create additional files
        api_doc = os.path.join(tmpdir, "api.md")
        guide_doc = os.path.join(tmpdir, "guide.md")

        with open(api_doc, "w") as f:
            f.write("# API Documentation\n\nREST API for integrations.")

        with open(guide_doc, "w") as f:
            f.write("# User Guide\n\nHow to get started.")

        # Add them
        kb.add([api_doc, guide_doc])
        print(f"Added 2 more documents. Total chunks: {kb.count()}")

        # Update both
        with open(api_doc, "w") as f:
            f.write(
                "# API Documentation\n\nREST API v2 with GraphQL support (updated!)."
            )

        with open(guide_doc, "w") as f:
            f.write("# User Guide\n\nQuick start guide (updated!).")

        # Refresh both at once
        kb.refresh([api_doc, guide_doc])
        print(f"Refreshed 2 documents. Total chunks: {kb.count()}")

        print("\n" + "=" * 60)
        print("Best Practices for Updates")
        print("=" * 60)
        print(
            """
1. Use refresh() for specific documents that changed
   → Efficient, only re-embeds what changed

2. Use clear() + add() for complete rebuild
   → When you want to start fresh

3. Track your sources in a list
   → Makes it easy to refresh selectively

Example pattern:
```python
sources = ["./docs/api.md", "./docs/guide.md", "./blog/*.md"]
kb = Ragi(sources)

# Later, when api.md changes:
kb.refresh("./docs/api.md")

# Or refresh all blog posts:
kb.refresh("./blog/*.md")
```
"""
        )

        print("\n✅ Update workflow examples completed!")


if __name__ == "__main__":
    main()
