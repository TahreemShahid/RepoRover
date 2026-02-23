"""
repo_loader.py — Clone a GitHub repo and feed Python files into CodeGraph.
"""
import os
import shutil
import tempfile
import subprocess
from pathlib import Path
from graph_engine import CodeGraph


MAX_FILE_SIZE_BYTES = 150_000   # skip files larger than ~150 KB
MAX_FILES = 200                  # cap total files to avoid blowing up memory


def _is_valid_github_url(url: str) -> bool:
    url = url.strip().rstrip("/")
    return "github.com" in url and len(url.split("/")) >= 5


def _normalize_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url.endswith(".git"):
        url += ".git"
    return url


def clone_and_build_graph(github_url: str, progress_callback=None) -> tuple[CodeGraph, dict]:
    """
    Clone a public GitHub repo, parse all Python files, build a CodeGraph.
    Returns (graph, info_dict).
    progress_callback(message: str) is called with status updates.
    """
    if not _is_valid_github_url(github_url):
        raise ValueError("Please provide a valid public GitHub URL, e.g. https://github.com/user/repo")

    url = _normalize_url(github_url)
    tmpdir = tempfile.mkdtemp(prefix="reporover_")

    def log(msg):
        if progress_callback:
            progress_callback(msg)

    try:
        log(f"📥 Cloning repository...")
        result = subprocess.run(
            ["git", "clone", "--depth=1", "--single-branch", url, tmpdir],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git clone failed: {result.stderr.strip()}")

        log("🔍 Scanning Python files...")
        py_files = list(Path(tmpdir).rglob("*.py"))

        # Filter out common non-useful dirs
        skip_dirs = {"__pycache__", ".git", "node_modules", "venv", ".venv", "env", "migrations", "test", "tests"}
        py_files = [
            f for f in py_files
            if not any(part in skip_dirs for part in f.parts)
            and f.stat().st_size < MAX_FILE_SIZE_BYTES
        ][:MAX_FILES]

        if not py_files:
            raise RuntimeError("No Python files found in this repository.")

        graph = CodeGraph()
        parsed_files = 0
        skipped = 0

        for i, filepath in enumerate(py_files):
            rel_path = str(filepath.relative_to(tmpdir))
            log(f"⚙️  Parsing ({i+1}/{len(py_files)}): {rel_path}")
            try:
                code = filepath.read_text(encoding="utf-8", errors="ignore")
                count = graph.add_file(rel_path, code)
                if count > 0:
                    parsed_files += 1
                else:
                    skipped += 1
            except Exception:
                skipped += 1
                continue

        stats = graph.get_stats()
        info = {
            "repo_url": github_url,
            "total_py_files": len(py_files),
            "parsed_files": parsed_files,
            "skipped_files": skipped,
            **stats,
        }

        log(f"✅ Done! Parsed {parsed_files} files → {stats['functions']} functions, {stats['classes']} classes")
        return graph, info

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
