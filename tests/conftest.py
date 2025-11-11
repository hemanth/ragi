"""Pytest configuration and fixtures."""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file."""
    file_path = os.path.join(temp_dir, "sample.txt")
    content = """# Sample Document

This is a sample document for testing.

## Section 1

This section contains information about feature A.

## Section 2

This section contains information about feature B.
"""
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture
def sample_markdown_file(temp_dir):
    """Create a sample markdown file."""
    file_path = os.path.join(temp_dir, "README.md")
    content = """# API Documentation

## Authentication

Use API keys for authentication.

## Endpoints

### GET /users
Returns a list of users.

### POST /users
Creates a new user.
"""
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture
def sample_code_file(temp_dir):
    """Create a sample code file."""
    file_path = os.path.join(temp_dir, "example.py")
    content = '''"""Example module."""

def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

class Calculator:
    """A simple calculator."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
'''
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture(autouse=True)
def mock_llm_env(monkeypatch):
    """Mock LLM environment variables for tests."""
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("LLM_API_KEY", "not-needed")
