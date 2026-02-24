# 🛰️ RepoRover

**Chat with any public GitHub repository using AI.**  
No database. No setup. Just bring your Groq API key.

## How it works

1. Paste a public GitHub repo URL
2. RepoRover clones it and parses **all files** (Python, JavaScript, config files, Markdown, and more)
3. Builds an in-memory code graph using NetworkX (Python files get function/class extraction via Tree-sitter)
4. You chat — questions are answered by Groq (Llama 3.3) using the graph as context

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tech Stack

- **Streamlit** — UI
- **Tree-sitter** — Python code parsing (functions & classes)
- **NetworkX** — In-memory code graph
- **LangChain + Groq** — LLM question answering (Llama 3.3 70B)

## Architecture

```
User pastes GitHub URL
        ↓
git clone --depth=1 (tmpdir)
        ↓
Scan all files (exclude binaries: images, archives, etc.)
        ↓
Python files → Tree-sitter parses functions & classes
Other files → Raw content stored as single entity
        ↓
NetworkX graph: File --[DEFINES]--> CodeEntity
        ↓
User asks a question
        ↓
Smart context extraction from graph
        ↓
Groq LLM answers with graph context
        ↓
tmpdir deleted after clone
```

## Supported Files

- **Python (`.py`)** — Full parsing of functions and classes
- **All other text files** — JavaScript, TypeScript, JSON, YAML, MD, HTML, CSS, configs, etc. (stored as raw content)
- Binary files (images, archives, fonts) are automatically skipped

## Limitations

- Public repos only
- Large repos may be slow on free hosting
- Graph lives in memory — cleared on session end
