def build_answer(context_chunks: list) -> str:
    if not context_chunks:
        return "No relevant passage found for this question."

    top_chunk = context_chunks[0]
    if isinstance(top_chunk, dict):
        return top_chunk.get("text", "").strip()
    elif isinstance(top_chunk, str):
        return top_chunk.strip()
    return str(top_chunk).strip()
