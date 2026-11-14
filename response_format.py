
"""Format KIWi responses and handle source visibility."""

import re


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
