import chromadb
import ollama

import config

client = ollama.Client(host=config.OLLAMA_HOST)
collection = chromadb.PersistentClient(path=config.CHROMA_DIR).get_collection(config.COLLECTION)


def retrieve(query, k=config.TOP_K):
    q_emb = client.embed(model=config.EMBED_MODEL, input=[query])["embeddings"][0]
    res = collection.query(query_embeddings=[q_emb], n_results=k * 4)   # over-fetch
    hits, seen = [], set()
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        key = " ".join(doc.split())[:150].lower()    # fingerprint of the chunk's opening
        if key in seen:
            continue                                  # near-duplicate of a closer hit
        seen.add(key)
        hits.append({
            "text": doc,
            "source": meta["source"],
            "page": meta["page"],
            "also_in": meta["also_in"],
            "distance": dist,
        })
        if len(hits) == k:
            break
    return hits


SYSTEM_PROMPT = """You are KIWi, a knowledge assistant for THWS staff.
Answer ONLY from the numbered context passages below.
- Cite the passages you used like [1], [2].
- If the context does not contain the answer, say you could not find it in the documents. Do not guess.
- If passages conflict (for example different issues of a newsletter give different dates), say so and prefer the most recent issue.
- Answer in the same language as the question. Be concise."""


def build_prompt(query, hits):
    parts = []
    for i, h in enumerate(hits, 1):
        parts.append(f"[{i}] (source: {h['source']}, page {h['page']})\n{h['text']}")
    context = "\n\n".join(parts)
    return f"Context:\n{context}\n\nQuestion: {query}"


def answer(query, k=config.TOP_K):
    hits = retrieve(query, k)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_prompt(query, hits)},
    ]
    resp = client.chat(model=config.LLM_MODEL, messages=messages,
                       options={"temperature": 0.1})
    return resp["message"]["content"], hits

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    show_chunks = "--chunks" in args
    query = " ".join(a for a in args if a != "--chunks") or "What is the deadline for HAW-ForschungsSchub?"

    if show_chunks:                      # debug mode: only show retrieval
        for i, h in enumerate(retrieve(query), 1):
            print(f"[{i}] {h['source']} p.{h['page']}  distance={h['distance']:.3f}")
            print(h["text"][:250].replace("\n", " "))
            print()
    else:                                # normal mode: full RAG answer
        text, hits = answer(query)
        print(text)
        print("\nSources:")
        for i, h in enumerate(hits, 1):
            print(f"  [{i}] {h['source']} p.{h['page']}  distance={h['distance']:.3f}")