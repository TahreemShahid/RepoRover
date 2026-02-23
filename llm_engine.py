"""
llm_engine.py — Answer questions about the code graph using Groq + LangChain.
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

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
    q = question.lower()

    # 1. Search by exact name first (most targeted)
    words = [w for w in question.split() if len(w) > 3]
    for word in words:
        results = graph.search_by_name(word)
        if results:
            lines = [f"ENTITIES MATCHING '{word}':"]
            for r in results:
                kind = "class" if r["type"] == "class_definition" else "function"
                lines.append(f"\n--- [{kind}] {r['name']} in {r['filename']} ---")
                # Send the actual full code block, not just the first line!
                lines.append(r['content'])
            return "\n".join(lines)

    # 2. Fallback: full graph context with larger previews
    lines = []
    for filename in graph.get_all_files():
        entities = graph.get_entities_in_file(filename)
        if not entities:
            continue
        lines.append(f"\n📄 FILE: {filename}")
        for e in entities:
            kind = "class" if e["type"] == "class_definition" else "function"
            lines.append(f"  [{kind}] {e['name']}  (line {e.get('start_line', '?')})")
            # Provide 10 lines instead of 3 so the AI can actually see methods
            preview = "\n".join(e["content"].splitlines()[:10])
            lines.append(f"    {preview}\n    ...")
            
    return "\n".join(lines)
    
    # Fallback: full graph context
    return graph.to_context_string()
