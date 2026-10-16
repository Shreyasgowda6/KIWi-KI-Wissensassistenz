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


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) or "What is the deadline for HAW-ForschungsSchub?"
    for i, h in enumerate(retrieve(query), 1):
        print(f"[{i}] {h['source']} p.{h['page']}  distance={h['distance']:.3f}")
        print(h["text"] if i == 1 else h["text"][:250].replace("\n", " "))
        print()