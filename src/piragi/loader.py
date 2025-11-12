"""Document loading using markitdown."""

import glob
import os
from pathlib import Path
from typing import List, Union
from urllib.parse import urlparse

from markitdown import MarkItDown

from .types import Document


class DocumentLoader:
    """Load documents from various sources using markitdown."""

    def __init__(self) -> None:
        """Initialize the document loader."""
        self.converter = MarkItDown()

    def load(self, source: Union[str, List[str]]) -> List[Document]:
        """
        Load documents from file paths, URLs, or glob patterns.

        Args:
            source: Single path/URL, list of paths/URLs, or glob pattern

        Returns:
            List of loaded documents
        """
        if isinstance(source, str):
            sources = [source]
        else:
            sources = source

        documents = []
        for src in sources:
            documents.extend(self._load_single(src))

        return documents

    def _load_single(self, source: str) -> List[Document]:
        """Load from a single source (file, URL, or glob pattern)."""
        # Check if it's a URL
        if self._is_url(source):
            return [self._load_url(source)]

        # Check if it's a glob pattern
        if any(char in source for char in ["*", "?", "[", "]"]):
            return self._load_glob(source)

        # Single file
        if os.path.isfile(source):
            return [self._load_file(source)]

        # Directory - load all files
        if os.path.isdir(source):
            return self._load_directory(source)

        raise ValueError(f"Invalid source: {source}")

    def _is_url(self, source: str) -> bool:
        """Check if source is a URL."""
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _load_file(self, file_path: str) -> Document:
        """Load a single file."""
        try:
            result = self.converter.convert(file_path)
            content = result.text_content

            # Extract metadata
            metadata = {
                "filename": os.path.basename(file_path),
                "file_type": Path(file_path).suffix.lstrip("."),
                "file_path": os.path.abspath(file_path),
            }

            return Document(content=content, source=file_path, metadata=metadata)

        except Exception as e:
            raise RuntimeError(f"Failed to load file {file_path}: {e}")

    def _load_url(self, url: str) -> Document:
        """Load content from a URL."""
        try:
            result = self.converter.convert(url)
            content = result.text_content

            metadata = {
                "filename": url.split("/")[-1] or "index",
                "file_type": "url",
                "file_path": url,
            }

            return Document(content=content, source=url, metadata=metadata)

        except Exception as e:
            raise RuntimeError(f"Failed to load URL {url}: {e}")

    def _load_glob(self, pattern: str) -> List[Document]:
        """Load files matching a glob pattern."""
        files = glob.glob(pattern, recursive=True)
        files = [f for f in files if os.path.isfile(f)]

        if not files:
            raise ValueError(f"No files found matching pattern: {pattern}")

        return [self._load_file(f) for f in files]

    def _load_directory(self, directory: str) -> List[Document]:
        """Load all files from a directory recursively."""
        pattern = os.path.join(directory, "**", "*")
        files = glob.glob(pattern, recursive=True)
        files = [f for f in files if os.path.isfile(f)]

        if not files:
            raise ValueError(f"No files found in directory: {directory}")

        documents = []
        for f in files:
            try:
                documents.append(self._load_file(f))
            except Exception:
                # Skip files that can't be processed
                continue

        return documents
