import os
from pathlib import Path

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_db")
COLLECTION = "kiwi"

# CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 900))
# CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 150))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
TOP_K = int(os.getenv("TOP_K", 5))
