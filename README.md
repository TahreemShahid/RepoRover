# 🛰️ RepoRover

**Chat with any public GitHub repository using AI.**  
No database. No setup. Just bring your Groq API key.

## How it works

1. Paste a public GitHub repo URL
2. RepoRover clones it, parses all Python files with Tree-sitter
3. Builds an in-memory code graph using NetworkX
4. You chat — questions are answered by Groq (Llama 3.3) using the graph as context

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```


## Tech Stack

- **Streamlit** — UI
- **Tree-sitter** — Python code parsing
- **NetworkX** — In-memory code graph 
- **LangChain + Groq** — LLM question answering (Llama 3.3 70B)

## Architecture

```
User pastes GitHub URL
        ↓
git clone --depth=1 (tmpdir)
        ↓
Tree-sitter parses all .py files
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

## Limitations

- Public repos only
- Python files only (for now)
- Large repos (1000+ files) may be slow on free hosting
- Graph lives in memory — cleared on session end
