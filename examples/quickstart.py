"""Quickstart example for Ragi."""

from piragi import Ragi


def main():
    """Simple example demonstrating Ragi basics."""
    # Create a sample document
    with open("sample.txt", "w") as f:
        f.write(
            """
# Getting Started with Ragi

Ragi is a zero-setup RAG library that makes it easy to build question-answering
systems over your documents.

## Installation

Install Ragi using pip:
```
pip install ragi
```

## Quick Start

Here's how to get started:

1. Import Ragi
2. Load your documents
3. Ask questions

That's it!

## Features

- Auto-chunking of documents
- Built-in embeddings
- Smart citations
- Metadata filtering
"""
        )

    # Initialize Ragi with the sample document
    print("Loading documents...")
    kb = Ragi("sample.txt", config={
        "embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
    })

    print(f"Loaded {kb.count()} chunks\n")

    # Ask a question
    print("Question: How do I install Ragi?\n")
    answer = kb.ask("How do I install Ragi?")

    print("Answer:")
    print(answer.text)
    print("\nCitations:")
    for i, citation in enumerate(answer.citations, 1):
        print(f"\n{i}. Source: {citation.source}")
        print(f"   Relevance: {citation.score:.2%}")
        print(f"   Preview: {citation.preview}")

    # Use callable shorthand
    print("\n" + "=" * 60 + "\n")
    print("Question: What are the main features?\n")
    answer = kb("What are the main features?")

    print("Answer:")
    print(answer.text)

    # Clean up
    import os

    os.remove("sample.txt")
    kb.clear()


if __name__ == "__main__":
    main()
