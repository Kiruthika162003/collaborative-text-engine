"""Word diff: two texts compared by word, because readers read words.

A character diff of two drafts shows changed swift to
swi[f->g]t and helps nobody; a word diff shows swift ->
swig and reads like the note an editor would leave. This
module diffs two plain texts at word granularity using the
longest common subsequence of their word lists, the same
algorithm a line diff uses one level up, and renders the
three verbs every diff has: words kept, words dropped from
the old, words added in the new. Whitespace is preserved as
its own tokens rather than smashed, because a diff that
turns two spaces into one is editing while pretending to
report, and the collapse of a paragraph break is exactly
the change a writer most wants to see. The summary counts
the three verbs, and the similarity is common words over
total words, a number for sorting revisions and never for
grading them, since the loom measures prose and refuses to
judge it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TOKEN = re.compile(r"\s+|\S+")


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text)


@dataclass(frozen=True)
class Span:
    verb: str
    text: str


def _lcs(old: list[str], new: list[str]) -> list[list[int]]:
    rows, cols = len(old) + 1, len(new) + 1
    table = [[0] * cols for _ in range(rows)]
    for i in range(len(old) - 1, -1, -1):
        for j in range(len(new) - 1, -1, -1):
            if old[i] == new[j]:
                table[i][j] = table[i + 1][j + 1] + 1
            else:
                table[i][j] = max(
                    table[i + 1][j], table[i][j + 1]
                )
    return table


def word_diff(old_text: str, new_text: str) -> list[Span]:
    old = tokenize(old_text)
    new = tokenize(new_text)
    table = _lcs(old, new)
    spans: list[Span] = []
    i = j = 0
    while i < len(old) and j < len(new):
        if old[i] == new[j]:
            spans.append(Span("kept", old[i]))
            i += 1
            j += 1
        elif table[i + 1][j] >= table[i][j + 1]:
            spans.append(Span("dropped", old[i]))
            i += 1
        else:
            spans.append(Span("added", new[j]))
            j += 1
    while i < len(old):
        spans.append(Span("dropped", old[i]))
        i += 1
    while j < len(new):
        spans.append(Span("added", new[j]))
        j += 1
    return spans


def summary(old_text: str, new_text: str) -> dict:
    spans = word_diff(old_text, new_text)
    kept = sum(
        1
        for s in spans
        if s.verb == "kept" and s.text.strip()
    )
    dropped = sum(
        1
        for s in spans
        if s.verb == "dropped" and s.text.strip()
    )
    added = sum(
        1
        for s in spans
        if s.verb == "added" and s.text.strip()
    )
    total = kept + dropped + added
    return {
        "kept": kept,
        "dropped": dropped,
        "added": added,
        "similarity": (
            round(kept / total, 3) if total else 1.0
        ),
    }


def render(old_text: str, new_text: str) -> str:
    parts = []
    for span in word_diff(old_text, new_text):
        if not span.text.strip():
            if span.verb in ("kept", "added"):
                parts.append(span.text)
            continue
        if span.verb == "kept":
            parts.append(span.text)
        elif span.verb == "dropped":
            parts.append(f"[-{span.text}-]")
        else:
            parts.append(f"[+{span.text}+]")
    return "".join(parts)
