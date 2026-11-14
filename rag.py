
import chromadb
import ollama
import config
import re
from time import perf_counter
from kiwi_logging import logger
from response_format import prepare_response, is_no_answer

logger.info("Initializing Ollama client and opening the knowledge index")
client = ollama.Client(host=config.OLLAMA_HOST)

collection = chromadb.PersistentClient(
    path=config.CHROMA_DIR
).get_collection(config.COLLECTION)
logger.info("Knowledge index ready: %s", config.COLLECTION)

CSV_METADATA_FIELDS = {
    "source",
    "record_id",
    "section",
    "source_url",
    "source_last_verified",
}


def validate_csv_metadata(metadata):
    missing = CSV_METADATA_FIELDS - metadata.keys()
    if missing:
        raise RuntimeError(
            "The ChromaDB index is from the previous data format and cannot be "
            "used with CSV data. Rebuild it by running `python ingest.py`, then "
            "restart with `python rag.py`."
        )


def retrieve(query, k=config.TOP_K):
    started = perf_counter()
    logger.info("Embedding question with %s", config.EMBED_MODEL)
    q_emb = client.embed(
        model=config.EMBED_MODEL,
        input=[query]
    )["embeddings"][0]

    logger.info("Embedding ready in %.2fs; searching ChromaDB for %d candidates", perf_counter() - started, k * 4)
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
        validate_csv_metadata(meta)
        key = " ".join(doc.split())[:150].lower()

        if key in seen:
            continue

        seen.add(key)

        hits.append({
            "text": doc,
            "source": meta["source"],
            "record_id": meta["record_id"],
            "section": meta["section"],
            "source_url": meta["source_url"],
            "source_last_verified": meta["source_last_verified"],
            "distance": dist
        })

        if len(hits) == k:
            break

    logger.info("Retrieval finished: %d passages selected in %.2fs", len(hits), perf_counter() - started)
    return hits


def format_source(hit):
    parts = [hit["source"], f"record {hit['record_id']}"]
    if hit["section"]:
        parts.append(hit["section"])
    if hit["source_last_verified"]:
        parts.append(f"verified {hit['source_last_verified']}")
    if hit["source_url"]:
        parts.append(hit["source_url"])
    return "; ".join(parts)


def add_source_link(text, hits):
    if is_no_answer(text):
        return prepare_response(text, hits)[0]
    if any(hit["source_url"] and hit["source_url"] in text for hit in hits):
        return text

    # Retrieval rank alone is not evidence that a source supports the answer.
    # Only add links for passages the response explicitly cites.
    cited = dict.fromkeys(int(number) for number in re.findall(r"\[(\d+)\]", text))
    for number in cited:
        if not 1 <= number <= len(hits):
            continue
        hit = hits[number - 1]
        if hit["source_url"]:
            label = hit["section"] or hit["source"]
            return f"{text.rstrip()}\n\n[{label}]({hit['source_url']})"
    return text


SYSTEM_PROMPT = """You are KIWi, a knowledge assistant for THWS staff.
Answer ONLY from the numbered context passages below.
- Cite the passages you used like [1], [2].
- Silently understand obvious spelling mistakes and repeated letters. Do not announce typos or ask the user to correct them when the meaning is clear.
- If a term could refer to multiple offices, faculties, or campuses, ask one short, specific clarifying question before giving directions. For example, for an unclear "dekant" location query, ask whether they mean the Dekanat (dean's office) and which faculty or campus. Do not assume a location.
- If the context does not contain the answer, briefly say you could not find it in the available information. Do not guess, describe unrelated retrieved material, or attach unrelated citations or links. Ask a useful clarification only when it could resolve the question.
- If passages conflict, say so and prefer the most recently verified source when dates are available.
- Answer in the same language as the question.
- Use the recent conversation to interpret short replies as answers to your previous clarification. Do not restart the topic or explain an acronym when the user is supplying it as a detail. Acknowledge supplied details and ask only for what is still missing. Prior conversation is not evidence for university facts; ground those facts in the current passages only.
- Lead with the direct answer. Use one or two sentences for simple factual questions. Give numbered steps or additional details only for questions that need them. Avoid phrases such as "based on the context provided" and do not pad the response.
- When the sources support an answer, include a direct Markdown link to the supporting source website using its URL from the context. Do not link to a source merely because it was retrieved."""


def build_prompt(query, hits):
    parts = []

    for i, h in enumerate(hits, 1):
        parts.append(
            f"[{i}] (source: {format_source(h)})\n{h['text']}"
        )

    context = "\n\n".join(parts)

    return f"Context:\n{context}\n\nQuestion: {query}"


def recent_history(history):
    return [
        {"role": item["role"], "content": item["content"][:4000]}
        for item in (history or [])
        if item.get("role") in {"user", "assistant"}
        and isinstance(item.get("content"), str)
        and not item.get("error")
    ][-8:]


def contextualize_query(query, history):
    if not history:
        return query
    logger.info("Interpreting follow-up using %d recent messages", len(history))
    response = client.chat(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": (
                "Rewrite the latest user message as one standalone search question, using "
                "the conversation only to resolve references and short clarification replies. "
                "Preserve the user's intent and language. Keep the original question if the "
                "user changed topic. Do not answer, invent a faculty, campus, address, or any "
                "missing detail. Return only the search question. For example, after asking "
                "which faculty's dean's office, the reply 'THWS' means the user is still "
                "looking for a dean's office at THWS, not asking what THWS stands for."
            )},
            *history,
            {"role": "user", "content": query},
        ],
        options={"temperature": 0, "num_predict": 160},
    )
    rewritten = response["message"]["content"].strip()
    return rewritten if rewritten and len(rewritten) <= 1200 else query


def answer(query, k=config.TOP_K, history=None):
    started = perf_counter()
    history = recent_history(history)
    search_query = contextualize_query(query, history)
    hits = retrieve(search_query, k)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": build_prompt(query, hits)}
    ]

    logger.info("Generating answer with %s using %d passages", config.LLM_MODEL, len(hits))
    generation_started = perf_counter()
    resp = client.chat(
        model=config.LLM_MODEL,
        messages=messages,
        options={"temperature": 0.1}
    )

    logger.info("Generation finished in %.2fs; formatting answer and source links", perf_counter() - generation_started)
    text = add_source_link(resp["message"]["content"], hits)
    text, hits = prepare_response(text, hits)
    logger.info("Answer ready: %d characters, %d source passages, %.2fs total", len(text), len(hits), perf_counter() - started)
    return text, hits


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

            text, hits = answer(query)

            print("KIWi:", text)

            if hits:
                print("\nSources:")

                for i, h in enumerate(hits, 1):
                    print(
                        f"  [{i}] {format_source(h)} "
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
