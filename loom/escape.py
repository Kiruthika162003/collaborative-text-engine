"""Escape: make arbitrary text safe to embed as literal Markdown, and undo it exactly.

Dropping a user's text into a Markdown document is dangerous
if the text holds a star or an underscore, because the
renderer will read them as formatting the writer never meant.
Escaping backslash-protects the inline characters that would
be misread, so the text renders as itself, and unescaping is
the exact inverse, stripping the backslash back off so a round
trip returns precisely what went in, which is the property
that lets text be escaped for storage and unescaped for
editing without drift. The escape is context-free and honest
about it: it protects every one of the inline special
characters wherever they appear, which is always safe because
an escaped star is always a literal star, but it over-escapes,
backslashing a star in a spot the renderer would have left
alone anyway, so escaped text reads noisier than a human hand
would have written. The line-start specials, the hash of a
heading and the dash of a list, are left to a caller who
knows whether the text sits at a line start, because escaping
them everywhere would backslash the hyphen in a mid-sentence
range and the period after a mid-sentence abbreviation, doing
more harm than the rare line-start collision it would
prevent. The two functions are pure and each other's inverse,
which is the whole contract worth keeping.
"""

from __future__ import annotations

ESCAPABLE = frozenset("\\`*_[]<>~|")


def escape(text: str) -> str:
    return "".join(
        "\\" + char if char in ESCAPABLE else char for char in text
    )


def unescape(text: str) -> str:
    out: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if (
            char == "\\"
            and index + 1 < len(text)
            and text[index + 1] in ESCAPABLE
        ):
            out.append(text[index + 1])
            index += 2
        else:
            out.append(char)
            index += 1
    return "".join(out)


def needs_escape(text: str) -> bool:
    return any(char in ESCAPABLE for char in text)
