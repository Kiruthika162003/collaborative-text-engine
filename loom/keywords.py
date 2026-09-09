"""Keywords: the words a document is about, once the function words are set aside.

Raw word frequency, which the concordance gives, is topped
by the, of, and to in every document ever written, so it
tells a reader nothing about what this document is about.
Keyword extraction is frequency with the function words
removed, the articles and prepositions and auxiliaries that
carry grammar rather than subject, leaving the nouns and
verbs that actually name the topic. This keeps a stoplist of
those function words and counts what remains, folding case so
Weave and weave are one word and ranking by count, which
surfaces the terms the document returns to. The stoplist is a
blunt instrument and the module says so plainly: it drops
May and Will and Mark, which are function words in one
sentence and a person's name in the next, and it cannot tell
which without reading meaning it does not have. So the
keywords are offered as what frequency suggests once grammar
is set aside, not as a claim about importance, and a proper
name that happens to collide with a stopword is a known
casualty a caller can restore by trimming the list. Very
short tokens are dropped too, since a and I survive the
stoplist but name nothing, and the result is capped so a
caller asking what a document is about gets a handful of
words rather than its whole vocabulary sorted.
"""

from __future__ import annotations

import re

from loom.weave import Weave

WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")

STOPWORDS = frozenset(
    {
        "the", "a", "an", "and", "or", "but", "if", "then", "else",
        "of", "to", "in", "on", "at", "by", "for", "with", "from",
        "as", "is", "are", "was", "were", "be", "been", "being",
        "it", "its", "this", "that", "these", "those", "which",
        "who", "whom", "whose", "what", "when", "where", "why", "how",
        "i", "you", "he", "she", "we", "they", "me", "him", "her",
        "us", "them", "my", "your", "his", "our", "their",
        "do", "does", "did", "have", "has", "had", "not", "no",
        "so", "than", "too", "very", "can", "will", "would", "should",
        "could", "may", "might", "must", "shall", "here", "there",
        "up", "down", "out", "over", "into", "about", "just", "also",
    }
)

MIN_LENGTH = 2


def frequencies(weave: Weave) -> dict[str, int]:
    counts: dict[str, int] = {}
    for match in WORD.finditer(weave.text()):
        word = match.group(0).lower()
        if len(word) < MIN_LENGTH or word in STOPWORDS:
            continue
        counts[word] = counts.get(word, 0) + 1
    return counts


def keywords(weave: Weave, limit: int = 10) -> list[tuple[str, int]]:
    counts = frequencies(weave)
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:limit]


def top_terms(weave: Weave, limit: int = 10) -> list[str]:
    return [word for word, _count in keywords(weave, limit)]


def report(weave: Weave, limit: int = 10) -> str:
    ranked = keywords(weave, limit)
    if not ranked:
        return "no keywords; the document is all function words"
    body = ", ".join(f"{word} ({count})" for word, count in ranked)
    return (
        f"top {len(ranked)} keyword(s): {body}\n"
        "frequency with grammar set aside, not a claim about "
        "importance"
    )
