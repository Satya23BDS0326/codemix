from backend.retriever import get_embedding

vec = get_embedding(
    "AI jobs Hyderabad lo unnaya"
)

print(len(vec))