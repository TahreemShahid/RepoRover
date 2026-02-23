"""
llm_engine.py — Answer questions about the code graph using Groq + LangChain.
No Cypher, no Neo4j. We pass graph context directly to the LLM.
"""
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from graph_engine import CodeGraph


SYSTEM_PROMPT = """You are RepoRover, an expert code analyst. You have been given a structured map of a Python codebase.

The codebase map below shows every file, function, and class that was found, with line numbers and a short preview of each entity's code.

Your job is to answer the user's question accurately using ONLY the information in this map.
- Be specific: mention exact function names, class names, and file paths.
- If you can't find the answer in the map, say so clearly.
- Keep answers concise and developer-friendly.
- If the user asks to list things, use a simple bullet list.

CODEBASE MAP:
{context}
"""

def answer_question(question: str, graph: CodeGraph, api_key: str) -> dict:
    """
    Answer a natural language question about the codebase.
    Returns dict with 'answer' and 'context_used'.
    """
    llm = ChatGroq(api_key=api_key, model_name="llama-3.3-70b-versatile", temperature=0)

    # Build context — smart routing for common question types
    context = _build_smart_context(question, graph)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}")
    ])

    chain = prompt | llm
    response = chain.invoke({"context": context, "question": question})

    return {
        "answer": response.content,
        "context_length": len(context),
    }


def _build_smart_context(question: str, graph: CodeGraph) -> str:
    """
    Instead of dumping everything, try to give the LLM the most relevant context.
    """
    q = question.lower()

    # If asking about a specific file
    for filename in graph.get_all_files():
        short_name = filename.split("/")[-1].replace(".py", "")
        if short_name in q or filename in q:
            entities = graph.get_entities_in_file(filename)
            if entities:
                lines = [f"FILE: {filename}"]
                for e in entities:
                    kind = "class" if e["type"] == "class_definition" else "function"
                    lines.append(f"  [{kind}] {e['name']} (line {e.get('start_line', '?')})")
                    lines.append(f"    {e['content'].splitlines()[0]}")
                return "\n".join(lines)

    # If asking about classes only
    if any(word in q for word in ["class", "classes", "object", "inherit"]):
        classes = graph.get_classes()
        if classes:
            lines = ["CLASSES IN CODEBASE:"]
            for c in classes:
                lines.append(f"  {c['name']} in {c['filename']} (line {c.get('start_line','?')})")
                lines.append(f"    {c['content'].splitlines()[0]}")
            return "\n".join(lines)

    # If asking about functions only
    if any(word in q for word in ["function", "functions", "def ", "method"]):
        funcs = graph.get_functions()
        if funcs:
            lines = ["FUNCTIONS IN CODEBASE:"]
            for f in funcs:
                lines.append(f"  {f['name']} in {f['filename']} (line {f.get('start_line','?')})")
            return "\n".join(lines)

    # If searching by name
    words = [w for w in question.split() if len(w) > 3]
    for word in words:
        results = graph.search_by_name(word)
        if results:
            lines = [f"ENTITIES MATCHING '{word}':"]
            for r in results:
                kind = "class" if r["type"] == "class_definition" else "function"
                lines.append(f"  [{kind}] {r['name']} in {r['filename']}")
                lines.append(f"    {r['content'].splitlines()[0]}")
            return "\n".join(lines)

    # Fallback: full graph context
    return graph.to_context_string()
