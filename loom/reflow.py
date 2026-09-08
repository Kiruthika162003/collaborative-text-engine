"""Reflow: wrapping a paragraph to a column without ever losing a word.

Plain-text documents live in columns, and reflow rewraps a
paragraph to a width, greedily filling each line with as
many words as fit and breaking before the word that would
overflow. The one hard rule is the rule a careless wrapper
breaks: a word longer than the whole column is never
chopped to fit, it is placed alone on its own line and
allowed to overflow, because splitting a url or a long
identifier to meet a margin produces two broken tokens
where there was one whole one, and a wrapper that mangles
its input to obey a number has forgotten which of the two
matters. Existing single newlines inside a paragraph are
treated as spaces, since the writer's soft wraps are not
the reader's, but blank lines between paragraphs are
preserved, because those are structure and reflow rewraps
prose, not architecture. The width is validated as at
least one, a zero-width column being a request to print a
document one letter tall.
"""

from __future__ import annotations

from loom.errors import Invalid


def _wrap_paragraph(text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current: list[str] = []
    length = 0
    for word in words:
        if not current:
            current = [word]
            length = len(word)
            continue
        if length + 1 + len(word) <= width:
            current.append(word)
            length += 1 + len(word)
        else:
            lines.append(" ".join(current))
            current = [word]
            length = len(word)
    if current:
        lines.append(" ".join(current))
    return lines


def reflow(text: str, width: int) -> str:
    if width < 1:
        raise Invalid(
            "a column narrower than one letter is a "
            "request for a document one letter tall"
        )
    paragraphs = text.split("\n\n")
    wrapped = [
        "\n".join(
            _wrap_paragraph(
                paragraph.replace("\n", " "), width
            )
        )
        for paragraph in paragraphs
    ]
    return "\n\n".join(wrapped)


def longest_line(text: str) -> int:
    return max(
        (len(line) for line in text.split("\n")),
        default=0,
    )


def fits_within(text: str, width: int) -> bool:
    return all(
        len(line) <= width or len(line.split()) == 1
        for line in text.split("\n")
    )
