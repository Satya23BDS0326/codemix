import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("  CodeMix Dual-Model Misinformation Intelligence System")
    print("  Serving at: http://127.0.0.1:8000")
    print("=" * 60 + "\n", flush=True)
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
