"""Example: Ask questions about a codebase."""

import os
import tempfile
from piragi import Ragi


def create_sample_codebase(tmpdir):
    """Create a sample Python codebase."""
    # Create a simple module
    with open(os.path.join(tmpdir, "auth.py"), "w") as f:
        f.write(
            '''"""Authentication module."""

import hashlib
from typing import Optional


class User:
    """Represents a user in the system."""

    def __init__(self, username: str, password_hash: str):
        self.username = username
        self.password_hash = password_hash

    @classmethod
    def create(cls, username: str, password: str) -> "User":
        """Create a new user with hashed password."""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return cls(username, password_hash)


class AuthManager:
    """Manages user authentication."""

    def __init__(self):
        self.users = {}

    def register(self, username: str, password: str) -> User:
        """Register a new user."""
        if username in self.users:
            raise ValueError(f"User {username} already exists")

        user = User.create(username, password)
        self.users[username] = user
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        if username not in self.users:
            return None

        user = self.users[username]
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if user.password_hash == password_hash:
            return user

        return None
'''
        )

    # Create README
    with open(os.path.join(tmpdir, "README.md"), "w") as f:
        f.write(
            """# Sample Project

A simple authentication system.

## Usage

```python
from auth import AuthManager

# Create auth manager
auth = AuthManager()

# Register a user
auth.register("alice", "password123")

# Authenticate
user = auth.authenticate("alice", "password123")
```

## Security

Passwords are hashed using SHA-256 before storage.
"""
        )


def main():
    """Demonstrate code Q&A capabilities."""
    # Create temporary codebase
    with tempfile.TemporaryDirectory() as tmpdir:
        print("Creating sample codebase...")
        create_sample_codebase(tmpdir)

        # Load the codebase
        print("Loading codebase into Ragi...")
        kb = Ragi(tmpdir, config={
            "embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
        })

        print(f"Loaded {kb.count()} chunks from codebase\n")

        # Ask questions about the code
        questions = [
            "How do I register a new user?",
            "How are passwords stored?",
            "What classes are available?",
            "Show me how to authenticate a user",
        ]

        for question in questions:
            print("=" * 60)
            print(f"Q: {question}\n")

            answer = kb.ask(question, top_k=3)

            print(f"A: {answer.text}\n")

            print("Sources:")
            for citation in answer.citations:
                print(f"  - {citation.source} (relevance: {citation.score:.2%})")

            print()

        # Filter by file type
        print("=" * 60)
        print("Q: What's in the README?\n")

        answer = kb.filter(filename="README.md").ask("What's in the README?")
        print(f"A: {answer.text}\n")


if __name__ == "__main__":
    main()
