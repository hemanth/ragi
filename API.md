# API Reference

Complete API documentation for Ragi.

## Main Class

### `Ragi`

The main interface for creating and querying RAG systems.

```python
from ragi import Ragi
```

#### Constructor

```python
Ragi(
    sources: Union[str, List[str], None] = None,
    persist_dir: str = ".ragi",
    config: Optional[Dict[str, Any]] = None,
)
```

**Parameters:**
- `sources` - File paths, URLs, or glob patterns to load initially
- `persist_dir` - Directory to persist vector database (default: `.ragi`)
- `config` - Optional configuration dict with nested sections:
  - `llm` - LLM configuration:
    - `model` - Model name (default: `llama3.2`)
    - `api_key` - API key (default: env `LLM_API_KEY` or `"not-needed"`)
    - `base_url` - API base URL (default: env `LLM_BASE_URL` or `"http://localhost:11434/v1"`)
  - `embedding` - Embedding configuration:
    - `model` - Model name (default: `nvidia/llama-embed-nemotron-8b`)
    - `device` - Device to use for local models (default: auto-detect)
    - `base_url` - API base URL for remote embeddings (optional)
    - `api_key` - API key for remote embeddings (optional, defaults to env `EMBEDDING_API_KEY`)
  - `chunk` - Chunking configuration:
    - `size` - Target chunk size in tokens (default: 512)
    - `overlap` - Number of tokens to overlap (default: 50)

**Examples:**
```python
# Basic initialization (uses free local models)
kb = Ragi("./docs")

# With public embedding model
kb = Ragi("./docs", config={
    "embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
})

# Custom Ollama model
kb = Ragi("./docs", config={
    "llm": {"model": "mistral"},
    "embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
})

# With OpenAI-compatible API (LLM only, local embeddings)
kb = Ragi("./docs", config={
    "llm": {
        "model": "gpt-4o-mini",
        "api_key": "sk-...",
        "base_url": "https://api.openai.com/v1"
    },
    "embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
})

# With OpenAI for both LLM and embeddings
kb = Ragi("./docs", config={
    "llm": {
        "model": "gpt-4o-mini",
        "api_key": "sk-...",
        "base_url": "https://api.openai.com/v1"
    },
    "embedding": {
        "model": "text-embedding-3-small",
        "base_url": "https://api.openai.com/v1",
        "api_key": "sk-..."
    }
})

# Custom chunking
kb = Ragi("./docs", config={
    "chunk": {"size": 1024, "overlap": 100},
    "embedding": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
})

# Empty initialization (add documents later)
kb = Ragi(persist_dir=".my_kb")
kb.add("./docs")
```

#### Methods

##### `add(sources: Union[str, List[str]]) -> Ragi`

Add documents to the knowledge base.

**Parameters:**
- `sources` - File paths, URLs, or glob patterns

**Returns:** Self for chaining

**Examples:**
```python
# Single file
kb.add("./README.md")

# Multiple files
kb.add(["./docs/*.pdf", "./src/**/*.py"])

# Chaining
kb.add("./docs").add("./src")

# URLs
kb.add("https://example.com/guide")
```

##### `ask(query: str, top_k: int = 5, system_prompt: Optional[str] = None) -> Answer`

Ask a question and get an answer with citations.

**Parameters:**
- `query` - Question to ask
- `top_k` - Number of relevant chunks to retrieve (default: 5)
- `system_prompt` - Custom system prompt for answer generation

**Returns:** `Answer` object with text and citations

**Examples:**
```python
answer = kb.ask("How do I install this?")
print(answer.text)

# More context
answer = kb.ask("How does auth work?", top_k=10)

# Custom prompt
prompt = "Answer concisely with code examples when relevant."
answer = kb.ask("Show me usage examples", system_prompt=prompt)
```

##### `__call__(query: str, top_k: int = 5) -> Answer`

Callable shorthand for `ask()`.

**Parameters:**
- `query` - Question to ask
- `top_k` - Number of relevant chunks to retrieve

**Returns:** `Answer` object

**Examples:**
```python
# These are equivalent:
answer = kb.ask("What is this?")
answer = kb("What is this?")
```

##### `filter(**kwargs) -> Ragi`

Filter documents by metadata for the next query.

**Parameters:**
- `**kwargs` - Metadata key-value pairs to filter by

**Returns:** Self for chaining

**Examples:**
```python
# Filter by file type
answer = kb.filter(file_type="pdf").ask("What's in the PDFs?")

# Filter by custom metadata
answer = kb.filter(category="api", version="v2").ask("How does it work?")

# Multiple filters
answer = kb.filter(author="Alice", topic="security").ask("Security guidelines?")
```

##### `count() -> int`

Return the number of chunks in the knowledge base.

**Returns:** Number of chunks

**Examples:**
```python
print(f"Knowledge base contains {kb.count()} chunks")
```

##### `refresh(sources: Union[str, List[str]]) -> Ragi`

Refresh specific sources by deleting old chunks and re-adding. Useful when documents have been updated.

**Parameters:**
- `sources` - File paths, URLs, or glob patterns to refresh

**Returns:** Self for chaining

**Examples:**
```python
# Refresh a single file
kb.refresh("./docs/api.md")

# Refresh multiple files
kb.refresh(["./docs/*.pdf", "./README.md"])

# Refresh after editing
with open("./docs/guide.md", "w") as f:
    f.write("Updated content...")
kb.refresh("./docs/guide.md")
```

##### `clear() -> None`

Clear all data from the knowledge base.

**Examples:**
```python
kb.clear()
print(kb.count())  # 0
```

## Data Types

### `Answer`

Result from a query with answer text and citations.

**Attributes:**
- `text: str` - The generated answer
- `citations: List[Citation]` - Source citations
- `query: str` - Original query

**Methods:**
- `__str__()` - Returns answer text
- `__repr__()` - Returns detailed representation

**Examples:**
```python
answer = kb.ask("What is RAG?")

print(answer.text)              # The answer
print(answer.query)             # "What is RAG?"
print(len(answer.citations))    # Number of citations

# String representation
print(answer)                   # Same as answer.text
print(repr(answer))             # Answer(text='...', citations=3)
```

### `Citation`

A single source citation with relevance score.

**Attributes:**
- `source: str` - Source file path or URL
- `chunk: str` - The actual text chunk
- `score: float` - Relevance score (0-1, higher is better)
- `metadata: Dict[str, Any]` - Additional metadata

**Properties:**
- `preview: str` - Preview of chunk (first 100 chars)

**Examples:**
```python
for citation in answer.citations:
    print(f"Source: {citation.source}")
    print(f"Score: {citation.score:.2%}")
    print(f"Preview: {citation.preview}")
    print(f"Metadata: {citation.metadata}")
```

## Supported File Formats

Ragi uses [markitdown](https://github.com/microsoft/markitdown) for document conversion and supports:

### Documents
- PDF (`.pdf`)
- Microsoft Word (`.docx`, `.doc`)
- Microsoft PowerPoint (`.pptx`, `.ppt`)
- Microsoft Excel (`.xlsx`, `.xls`)

### Text
- Markdown (`.md`)
- Plain text (`.txt`)
- Source code (`.py`, `.js`, `.java`, `.cpp`, etc.)
- HTML (`.html`)

### Data
- JSON (`.json`)
- XML (`.xml`)
- CSV (`.csv`)

### Media
- Images (`.png`, `.jpg`, `.jpeg`, `.gif`) - with OCR
- Audio (`.mp3`, `.wav`) - with transcription

### Web
- URLs (converted to markdown)

### Archives
- ZIP files (`.zip`)

### E-books
- EPub (`.epub`)

## Metadata Fields

### Automatic Metadata

Automatically extracted for all documents:
- `filename` - File name
- `file_type` - File extension without dot
- `file_path` - Absolute file path

For URLs:
- `url` - The URL
- `source_type` - Always "url"

### Custom Metadata

Add custom metadata when loading:
```python
# This is a planned feature
kb.add("./docs/api.pdf", metadata={"category": "api", "version": "v2"})
```

Filter by custom metadata:
```python
answer = kb.filter(category="api").ask("How does it work?")
```

## Error Handling

### Common Exceptions

```python
# Invalid source
try:
    kb = Ragi("/nonexistent/path")
except ValueError as e:
    print(f"Error: {e}")

# Missing API key
try:
    kb = Ragi("./docs")
except RuntimeError as e:
    print(f"Error: {e}")

# Embedding generation failed
try:
    answer = kb.ask("question")
except RuntimeError as e:
    print(f"Error: {e}")
```

## Environment Variables

- `LLM_BASE_URL` - LLM API base URL (default: `http://localhost:11434/v1`)
- `LLM_API_KEY` - LLM API key (default: `not-needed`)

For Ollama (default, free local models):
```bash
# No environment variables needed!
# Just make sure Ollama is running: ollama serve
```

For OpenAI or other providers:
```bash
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_API_KEY="sk-..."
```

Or in `.env` file:
```
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-...
```

## Best Practices

### Chunking
- Use smaller chunks (256-512) for precise retrieval
- Use larger chunks (1024+) when more context is needed
- Increase overlap (100-200) for better continuity

### Embeddings
- Use `sentence-transformers/all-MiniLM-L6-v2` for free, fast embeddings (recommended for getting started)
- Use `nvidia/llama-embed-nemotron-8b` for higher quality (requires HuggingFace auth)
- Use any sentence-transformers model from HuggingFace

### LLM Selection
- Use `llama3.2` via Ollama for free local inference (default)
- Use `mistral` via Ollama for fast responses
- Use OpenAI-compatible APIs for cloud-based models (configure via `config` dict)

### Performance
- Persist data to disk to avoid re-processing:
  ```python
  kb = Ragi("./docs", persist_dir=".kb")
  ```
- Batch document additions:
  ```python
  kb.add(["doc1.pdf", "doc2.pdf", "doc3.pdf"])
  ```
- Use appropriate `top_k` values (5-10 for most cases)

### Filtering
- Use metadata filters to narrow search space
- Combine filters for precise targeting:
  ```python
  kb.filter(type="api", version="v2").ask("...")
  ```

## Type Hints

Ragi is fully typed. Example:

```python
from typing import List
from ragi import Ragi, Answer, Citation

kb: Ragi = Ragi("./docs")
answer: Answer = kb.ask("What is this?")
citations: List[Citation] = answer.citations
```
