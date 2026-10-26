
import chromadb
import ollama
import config
from intent_classifier import classify_intent

client = ollama.Client(host=config.OLLAMA_HOST)

collection = chromadb.PersistentClient(
    path=config.CHROMA_DIR
).get_collection(config.COLLECTION)


def retrieve(query, k=config.TOP_K):
    q_emb = client.embed(
        model=config.EMBED_MODEL,
        input=[query]
    )["embeddings"][0]

    res = collection.query(
        query_embeddings=[q_emb],
        n_results=k * 4
    )

    hits, seen = [], set()

    for doc, meta, dist in zip(
        res["documents"][0],
        res["metadatas"][0],
        res["distances"][0]
    ):
        key = " ".join(doc.split())[:150].lower()

        if key in seen:
            continue

        seen.add(key)

        hits.append({
            "text": doc,
            "source": meta["source"],
            "page": meta["page"],
            "also_in": meta["also_in"],
            "distance": dist
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
        parts.append(
            f"[{i}] (source: {h['source']}, page {h['page']})\n{h['text']}"
        )

    context = "\n\n".join(parts)

    return f"Context:\n{context}\n\nQuestion: {query}"


def answer(query, k=config.TOP_K, *, show_intent=False):
    intent, classification_status = classify_intent(client, query)
    if show_intent:
        detail = "" if classification_status == "ok" else f" ({classification_status})"
        print(f"Intent: {intent}{detail}\n", flush=True)
    hits = retrieve(query, k)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_prompt(query, hits)}
    ]

    resp = client.chat(
        model=config.LLM_MODEL,
        messages=messages,
        options={"temperature": 0.1}
    )

    return resp["message"]["content"], hits


if __name__ == "__main__":
    print("KIWi - THWS Knowledge Assistant")
    print("Ask a question or type 'exit' to quit.\n")

    while True:
        try:
            query = input("You: ").strip()

            if query.lower() in ("exit", "quit"):
                print("KIWi: Goodbye!")
                break

            if not query:
                continue

            print("\nKIWi is searching your documents...\n")

            text, hits = answer(query, show_intent=True)

            print("KIWi:", text)

            if hits:
                print("\nSources:")

                for i, h in enumerate(hits, 1):
                    print(
                        f"  [{i}] {h['source']} "
                        f"p.{h['page']} "
                        f"distance={h['distance']:.3f}"
                    )
            else:
                print("\nNo relevant document passages were retrieved.")

            print()

        except KeyboardInterrupt:
            print("\nKIWi: Goodbye!")
            break

        except Exception as e:
            print(f"\nAn error occurred: {e}\n")
