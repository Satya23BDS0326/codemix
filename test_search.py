from backend.search import search

results = search(
    "What is ContrastiveMix?"
)

for i, r in enumerate(results):
    print(f"\nResult {i+1}")
    print(r[:500])