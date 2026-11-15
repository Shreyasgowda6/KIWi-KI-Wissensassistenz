
"""Format KIWi responses and handle source visibility."""

import re


def conversational_reply(text):
    """Handle standalone social messages without retrieving university sources."""
    normalized = " ".join(re.sub(r"[^\w\s]", "", text.casefold()).split())
    normalized = re.sub(r"\bkiwi\b", "", normalized).strip()
    normalized = " ".join(normalized.split())
    greetings = {"hi", "hello", "hey", "hi there", "hello there"}
    german = {"hallo", "guten morgen", "guten tag", "guten abend", "moin", "servus"}
    if normalized in greetings | german:
        return {
            "content": "Hallo! Wie kann ich dir bei Fragen zur THWS helfen?" if normalized in german
            else "Hi! I'm KIWi. How can I help you with THWS today?",
            "avatar": "greeting", "sources": [],
        }
    social = re.sub(r"^(?:hi|hello|hey|hallo)\s+", "", normalized)
    replies = {
        "how are you": "I'm ready to help! What would you like to know?",
        "how are you doing": "I'm ready to help! What would you like to know?",
        "how is it going": "I'm ready to help! What would you like to know?",
        "hows it going": "I'm ready to help! What would you like to know?",
        "wie gehts": "Ich bin bereit zu helfen! Was möchtest du wissen?",
        "wie geht es dir": "Ich bin bereit zu helfen! Was möchtest du wissen?",
        "wie gehts dir": "Ich bin bereit zu helfen! Was möchtest du wissen?",
        "thanks": "You're welcome!", "thank you": "You're welcome!",
        "danke": "Gern geschehen!", "bye": "Goodbye!", "tschüss": "Tschüss!",
    }
    if social in replies:
        return {"content": replies[social], "avatar": "default", "sources": []}
    return None


def is_no_answer(text):
    return bool(re.search(
        r"\b(?:i|we)\s+(?:could not|cannot|can't|couldn't|did not|didn't)\s+find\b"
        r"|\b(?:context|sources?|documents?|data)\s+"
        r"(?:does not|do not|doesn't|don't)\s+"
        r"(?:contain|provide|include|mention)\b"
        r"|\b(?:ich|wir)\s+"
        r"(?:kann|können|konnte|konnten|habe|haben)\b"
        r"[^.!?\n]{0,100}\bkeine?\b"
        r"[^.!?\n]{0,100}\b(?:finden|gefunden)\b",
        text,
        re.IGNORECASE,
    ))


def prepare_response(text, sources):
    """
    Keep retrieved sources available for factual answers.

    Remove sources for explicit no-answer responses.
    """

    if not is_no_answer(text):
        if text.rstrip().endswith("?") and re.match(
            r"(?:could you|can you|please specify|which faculty|which campus)", text, re.I
        ) and not re.search(r"\[\d+\]|https?://", text):
            return text, []
        return text, sources

    # Remove citations and links from no-answer responses.
    text = re.sub(
        r"\[[^\]]+\]\(https?://[^\s)]+\)",
        "",
        text
    )

    text = re.sub(
        r"https?://[^\s<>]+",
        "",
        text
    )

    text = re.sub(
        r"\[\d+\]",
        "",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    ).strip()

    return text, []
