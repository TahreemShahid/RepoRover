import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from langchain_core.documents import Document

PY_LANGUAGE = Language(tspython.language())


try:
    parser = Parser(PY_LANGUAGE)          # 0.23+ style
except TypeError:
    parser = Parser()                      # fallback for older builds
    parser.set_language(PY_LANGUAGE)


def get_function_and_class_chunks(code_source: str, filename: str = "unknown"):
    """
    Parses Python source code and returns LangChain Documents
    for each function and top-level class found.
    """
    tree = parser.parse(bytes(code_source, "utf8"))
    chunks = []
    cursor = tree.walk()

    while True:
        node = cursor.node

        if node.type in ["function_definition", "class_definition"]:
            start = node.start_byte
            end = node.end_byte
            chunk_text = code_source.encode("utf8")[start:end].decode("utf8")

            name = "unknown"
            for child in node.children:
                if child.type == "identifier":
                    name = code_source.encode("utf8")[child.start_byte:child.end_byte].decode("utf8")
                    break

            chunks.append(Document(
                page_content=chunk_text,
                metadata={
                    "type": node.type,
                    "name": name,
                    "start_line": node.start_point[0],
                    "filename": filename,
                }
            ))

            if node.type == "class_definition":
                if not cursor.goto_next_sibling():
                    break
                continue

        if cursor.goto_first_child():
            continue
        if cursor.goto_next_sibling():
            continue

        while True:
            if not cursor.goto_parent():
                return chunks
            if cursor.goto_next_sibling():
                break

    return chunks
