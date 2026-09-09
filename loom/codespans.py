"""Code spans: find the inline backtick code in text, pairing runs by length.

Inline code is delimited by backticks, and the rule that makes
it robust is the one CommonMark uses: a span is opened by a run
of some number of backticks and closed by the next run of
exactly that many, which is what lets a span that must contain
a backtick be written with two backticks around it, the inner
single one then being content rather than a delimiter. This
finds the spans that way, scanning the backtick runs and
pairing each opener with the next run of matching length, so a
double-backtick span correctly swallows a single backtick
inside it and a single-backtick span closes at the next single
backtick. The content returned is the text between the
delimiters exactly, unstripped, because the surrounding-space
trimming CommonMark does for rendering is a rendering concern
and a caller reading the code wants the characters that are
there. A backtick run with no matching run after it is an
unclosed span, reported rather than paired with a delimiter
that is not the right length, because guessing a close of the
wrong length would swallow half a document into a code span it
was never in. It reads inline spans and leaves fenced blocks to
the fences module, since a fence is a block construct with its
own rules and conflating the two would make each read the
other wrong.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

RUN = re.compile(r"`+")


@dataclass(frozen=True)
class Span:
    content: str
    start: int
    end: int


def spans(text: str) -> list[Span]:
    runs = [
        (match.start(), match.end(), match.end() - match.start())
        for match in RUN.finditer(text)
    ]
    found = []
    index = 0
    while index < len(runs):
        start, opener_end, length = runs[index]
        closer = index + 1
        while closer < len(runs) and runs[closer][2] != length:
            closer += 1
        if closer < len(runs):
            content = text[opener_end : runs[closer][0]]
            found.append(Span(content=content, start=start, end=runs[closer][1]))
            index = closer + 1
        else:
            index += 1
    return found


def contents(text: str) -> list[str]:
    return [span.content for span in spans(text)]


def unclosed(text: str) -> bool:
    matched = 2 * len(spans(text))
    total_runs = len(RUN.findall(text))
    return total_runs > matched
