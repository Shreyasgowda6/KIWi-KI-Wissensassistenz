import re
import pymupdf
import config
import hashlib
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import ollama


def clean(text):
    text = text.replace("\u00ad", "")                # remove invisible soft hyphens
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)     # join words split across lines
    text = re.sub(r"[ \t]+", " ", text)              # collapse repeated spaces
    text = re.sub(r" ?\n ?", "\n", text)             # strip spaces around line breaks
    text = re.sub(r"(?im)^focus\s+funding\s+\w+\s+\d{4}(\s+\d{1,3})?\s*$", "", text)  # page header
    text = re.sub(r"(?m)^\d{1,3}$", "", text)       # lone page numbers
    text = re.sub(r"\n{3,}", "\n\n", text)           # collapse many blank lines
    return text.strip()


def load_pages(path):
    with pymupdf.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            text = clean(page.get_text("text"))
            if len(text) > 40:                        # skip empty/near-empty pages
                yield i, text


def build_chunks():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = {}   # fingerprint -> chunk info
    total = 0
    for pdf in sorted(config.DATA_DIR.glob("**/*.pdf")):
        for page_no, text in load_pages(pdf):
            for piece in splitter.split_text(text):
                total += 1
                h = hashlib.sha1(piece.encode()).hexdigest()
                where = f"{pdf.name} p.{page_no}"
                if h in chunks:
                    chunks[h]["also_in"].append(where)
                else:
                    chunks[h] = {"text": piece, "source": pdf.name,
                                 "page": page_no, "also_in": []}
    return chunks, total


def build_index():
    chunks, total = build_chunks()
    print(f"{total} chunks -> {len(chunks)} unique")

    client = ollama.Client(host=config.OLLAMA_HOST)
    db = chromadb.PersistentClient(path=config.CHROMA_DIR)
    try:
        db.delete_collection(config.COLLECTION)   # rebuild from scratch every run
    except Exception:
        pass
    col = db.create_collection(config.COLLECTION, metadata={"hnsw:space": "cosine"})

    ids = list(chunks.keys())
    B = 32                                         # embed 32 chunks per request
    for s in range(0, len(ids), B):
        batch_ids = ids[s:s + B]
        batch = [chunks[i] for i in batch_ids]
        emb = client.embed(model=config.EMBED_MODEL,
                           input=[c["text"] for c in batch])["embeddings"]
        col.add(
            ids=batch_ids,
            embeddings=emb,
            documents=[c["text"] for c in batch],
            metadatas=[{"source": c["source"], "page": c["page"],
                        "also_in": "; ".join(c["also_in"])} for c in batch],
        )
        print(f"indexed {min(s + B, len(ids))}/{len(ids)}")
    print("Done. Stored in ChromaDB:", col.count(), "chunks")


if __name__ == "__main__":
    build_index()