"""Example: Working with multiple file formats."""

import json
import os
import tempfile
from piragi import Ragi


def create_sample_docs(tmpdir):
    """Create sample documents in different formats."""
    # Markdown documentation
    with open(os.path.join(tmpdir, "guide.md"), "w") as f:
        f.write(
            """# User Guide

## Introduction

Welcome to our product! This guide will help you get started.

## Features

- Real-time collaboration
- Cloud storage
- End-to-end encryption
- Mobile apps

## Pricing

- Free: Up to 5GB storage
- Pro: $10/month for 100GB
- Enterprise: Custom pricing
"""
        )

    # JSON configuration
    config = {
        "app_name": "MyApp",
        "version": "2.0.0",
        "api": {
            "base_url": "https://api.example.com",
            "timeout": 30,
            "rate_limit": 1000,
        },
        "features": {"collaboration": True, "encryption": True, "mobile": True},
    }

    with open(os.path.join(tmpdir, "config.json"), "w") as f:
        json.dump(config, f, indent=2)

    # Plain text
    with open(os.path.join(tmpdir, "changelog.txt"), "w") as f:
        f.write(
            """CHANGELOG

Version 2.0.0 (2024-01-15)
- Added real-time collaboration
- Improved mobile apps
- Enhanced security

Version 1.5.0 (2023-12-01)
- Added cloud storage
- Bug fixes
"""
        )


def main():
    """Demonstrate multi-format document loading."""
    with tempfile.TemporaryDirectory() as tmpdir:
        print("Creating sample documents...")
        create_sample_docs(tmpdir)

        # Load all documents
        print("Loading documents into Ragi...")
        kb = Ragi(tmpdir, config={
            "embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
        })

        print(f"Loaded {kb.count()} chunks from {tmpdir}\n")

        # Ask questions that span multiple documents
        questions = [
            "What pricing plans are available?",
            "What's the API rate limit?",
            "What features were added in version 2.0.0?",
            "Does it have mobile apps?",
        ]

        for question in questions:
            print("=" * 60)
            print(f"Q: {question}\n")

            answer = kb.ask(question)

            print(f"A: {answer.text}\n")

            # Show which files were used
            sources = {citation.source for citation in answer.citations}
            print(f"Information from {len(sources)} file(s):")
            for source in sources:
                filename = os.path.basename(source)
                print(f"  - {filename}")

            print()

        # Filter by file type
        print("=" * 60)
        print("Filtering by JSON files only:\n")

        answer = kb.filter(file_type="json").ask("What's in the configuration?")
        print(f"A: {answer.text}\n")


if __name__ == "__main__":
    main()
