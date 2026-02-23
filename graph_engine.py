"""
graph_engine.py — In-memory code graph using NetworkX.
Replaces Neo4j entirely. No database, no credentials, no cost.
Each Streamlit session gets its own graph instance.
"""
import networkx as nx
from pathlib import Path
from step1_parser import get_function_and_class_chunks


class CodeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_file(self, filename: str, code_source: str):
        """Parse a file and add its nodes/edges to the graph."""
        # Add File node
        self.graph.add_node(filename, node_type="file", name=filename)

        chunks = get_function_and_class_chunks(code_source, filename)
        for chunk in chunks:
            entity_id = f"{filename}::{chunk.metadata['name']}"
            self.graph.add_node(
                entity_id,
                node_type="code_entity",
                name=chunk.metadata["name"],
                type=chunk.metadata["type"],
                content=chunk.page_content,
                start_line=chunk.metadata["start_line"],
                filename=filename,
            )
            self.graph.add_edge(filename, entity_id, relation="DEFINES")

        return len(chunks)

    def clear(self):
        self.graph.clear()

    # ── Query helpers ──────────────────────────────────────────────────────────

    def get_all_files(self):
        return [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == "file"]

    def get_entities_in_file(self, filename: str):
        return [
            self.graph.nodes[n]
            for n in self.graph.successors(filename)
            if self.graph.nodes[n].get("node_type") == "code_entity"
        ]

    def get_all_entities(self):
        return [
            d for _, d in self.graph.nodes(data=True)
            if d.get("node_type") == "code_entity"
        ]

    def get_functions(self):
        return [e for e in self.get_all_entities() if e.get("type") == "function_definition"]

    def get_classes(self):
        return [e for e in self.get_all_entities() if e.get("type") == "class_definition"]

    def search_by_name(self, name: str):
        name_lower = name.lower()
        return [
            d for _, d in self.graph.nodes(data=True)
            if d.get("node_type") == "code_entity"
            and name_lower in d.get("name", "").lower()
        ]

    def get_stats(self):
        entities = self.get_all_entities()
        return {
            "files": len(self.get_all_files()),
            "functions": sum(1 for e in entities if e.get("type") == "function_definition"),
            "classes": sum(1 for e in entities if e.get("type") == "class_definition"),
            "total_entities": len(entities),
        }

    def to_context_string(self, max_entities: int = 60) -> str:
        """
        Serialize graph data into a compact string for the LLM context window.
        """
        lines = []
        for filename in self.get_all_files():
            entities = self.get_entities_in_file(filename)
            if not entities:
                continue
            lines.append(f"\n📄 FILE: {filename}")
            for e in entities:
                kind = "class" if e["type"] == "class_definition" else "function"
                lines.append(f"  [{kind}] {e['name']}  (line {e.get('start_line', '?')})")
                # Include first 3 lines of content as a hint
                preview = "\n".join(e["content"].splitlines()[:3])
                lines.append(f"    {preview}")

            if len(lines) > max_entities * 4:
                lines.append("  ... (truncated for brevity)")
                break

        return "\n".join(lines)
