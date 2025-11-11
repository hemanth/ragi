"""Example using Ragi with Ollama (free, local LLM)."""

import sys
import urllib.request
from piragi import Ragi


def check_ollama():
    """Check if Ollama is running."""
    try:
        urllib.request.urlopen("http://localhost:11434", timeout=2)
        return True
    except Exception:
        return False


def main():
    """Demonstrate Ragi with Ollama."""
    print("=" * 60)
    print("Ragi + Ollama Example")
    print("=" * 60)
    print()

    # Create a sample document
    print("Creating sample document...")
    with open("sample_doc.txt", "w") as f:
        f.write(
            """
# Product Documentation

## Overview
Our product is a cloud-based platform for managing customer data.

## Installation
To install:
1. Sign up at https://example.com
2. Download the CLI: `npm install -g our-cli`
3. Run: `our-cli init`

## Authentication
Use API keys for authentication:
- Generate a key in the dashboard
- Set environment variable: `export API_KEY=your-key`
- Use in requests: `Authorization: Bearer $API_KEY`

## Deployment
Deploy using:
```bash
our-cli deploy production
```

## Features
- Real-time sync
- Automatic backups
- Role-based access control
- Analytics dashboard
"""
        )

    print("✓ Sample document created\n")

    # Initialize Ragi with Ollama
    # Using a public embedding model (no auth required)
    print("Initializing Ragi with Ollama (llama3.2)...")
    kb = Ragi("sample_doc.txt", config={
        "embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
    })
    print(f"✓ Loaded {kb.count()} chunks\n")

    # Example 1: Basic question
    print("=" * 60)
    print("Example 1: Basic Question")
    print("=" * 60)
    question = "How do I install this product?"
    print(f"Q: {question}\n")

    answer = kb.ask(question)
    print(f"A: {answer.text}\n")

    print("Sources:")
    for i, citation in enumerate(answer.citations, 1):
        print(f"{i}. {citation.source} (relevance: {citation.score:.0%})")
        print(f"   Preview: {citation.preview}\n")

    # Example 2: Using callable shorthand
    print("=" * 60)
    print("Example 2: Callable Shorthand")
    print("=" * 60)
    question = "What features does it have?"
    print(f"Q: {question}\n")

    answer = kb(question)  # Same as kb.ask()
    print(f"A: {answer.text}\n")

    # Example 3: Using different Ollama model
    print("=" * 60)
    print("Example 3: Using Different Ollama Model")
    print("=" * 60)
    print("Trying to use 'mistral' model (if available)...\n")

    try:
        kb_mistral = Ragi("sample_doc.txt", config={
            "llm": {"model": "mistral"},
            "embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
        })

        question = "How does authentication work?"
        print(f"Q: {question}\n")

        answer = kb_mistral.ask(question)
        print(f"A: {answer.text}\n")
    except Exception as e:
        print(f"⚠️  Skipped: mistral model not available")
        print(f"   To use it: ollama pull mistral\n")

    # Example 4: Multiple sources
    print("=" * 60)
    print("Example 4: Multiple Sources")
    print("=" * 60)

    # Create another document
    with open("api_doc.txt", "w") as f:
        f.write(
            """
# API Reference

## Endpoints

### GET /users
Returns a list of all users.

### POST /users
Creates a new user.
Required fields: name, email

### DELETE /users/:id
Deletes a user by ID.
"""
        )

    print("Loading multiple documents...")
    kb_multi = Ragi(["sample_doc.txt", "api_doc.txt"], config={
        "embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
    })
    print(f"✓ Loaded {kb_multi.count()} chunks from multiple files\n")

    question = "What API endpoints are available?"
    print(f"Q: {question}\n")

    answer = kb_multi.ask(question)
    print(f"A: {answer.text}\n")

    # Cleanup
    import os
    os.remove("sample_doc.txt")
    os.remove("api_doc.txt")
    kb.clear()
    kb_multi.clear()

    print("=" * 60)
    print("✓ Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Ragi + Ollama Example")
    print("=" * 60 + "\n")

    # Check if Ollama is running
    print("Checking if Ollama is running...")
    if not check_ollama():
        print("❌ Ollama is not running!\n")
        print("Setup instructions:")
        print("  1. Install: curl -fsSL https://ollama.com/install.sh | sh")
        print("  2. Pull model: ollama pull llama3.2")
        print("  3. Start Ollama: ollama serve")
        print("  4. Run this script again\n")
        sys.exit(1)

    print("✓ Ollama is running\n")

    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  - Is Ollama running? Check: http://localhost:11434")
        print("  - Have you pulled llama3.2? Run: ollama pull llama3.2")
        print("  - Check Ollama logs: ollama logs")
        sys.exit(1)
