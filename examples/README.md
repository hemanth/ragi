# Ragi Examples

Quick examples demonstrating Ragi features.

## Basic Examples

### quickstart.py
Basic intro - load documents and ask questions.
```bash
python examples/quickstart.py
```

### ollama_example.py
Using Ragi with Ollama (free local LLM).
```bash
python examples/ollama_example.py
```

### code_qa.py
Question-answering over a Python codebase.
```bash
python examples/code_qa.py
```

### multi_format.py
Working with multiple document formats (Markdown, JSON, text).
```bash
python examples/multi_format.py
```

## Advanced Examples

### embedding_options.py
Different embedding configurations (local vs remote).
```bash
python examples/embedding_options.py
```

### update_documents.py
Manual document refresh workflow.
```bash
python examples/update_documents.py
```

### auto_update_detection.py
Automatic change detection for files and URLs.
```bash
python examples/auto_update_detection.py
```

## Setup

```bash
# Install Ragi
pip install ragi

# Install Ollama (for local LLM)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

## Quick Template

```python
from ragi import Ragi

# Load documents (auto-updates enabled by default)
kb = Ragi(["./docs", "https://api.example.com/docs"])

# Ask questions
answer = kb.ask("Your question")
print(answer.text)

# View citations
for cite in answer.citations:
    print(f"{cite.source} ({cite.score:.0%})")
```
