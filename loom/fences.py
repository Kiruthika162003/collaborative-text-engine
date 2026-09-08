"""Fences: the triple-backtick code blocks found so the rest of the tools skip them.

A fenced code block is text that means itself: the stars and
hashes inside it are code, not formatting, and every tool
that reads structure needs to know where the fences are so
it does not lint a shell script's hash as a heading or a
regex's asterisk as emphasis. This finds the fences the
CommonMark way, an opening line of three or more backticks
carrying an optional language, a closing line of at least as
many backticks and nothing else, and everything between
taken literally as the body. Each fence pins to its opening
line so a reference to the third code block survives edits
above it, and the line numbers of the body are reported so a
spell check or an emphasis parser can walk around the code
rather than through it. An unclosed fence, the one a writer
opened and never shut, runs to the end of the document and
is flagged rather than guessed shut, because a missing
closing fence is a real mistake a writer wants surfaced, and
silently closing it at the last line hides the error while
pretending the code block ended somewhere it did not. The
simplifications are named: tilde fences are not recognised
and neither are nested fences, because the backtick form is
what the room actually types, and a parser that handled
every exotic variant would be larger than the feature earns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from loom.ids import OpId
from loom.weave import Weave

OPEN = re.compile(r"^(`{3,})(.*)$")
CLOSE = re.compile(r"^(`{3,})\s*$")


@dataclass(frozen=True)
class Fence:
    language: str
    body: str
    start_pin: OpId
    open_line: int
    close_line: int | None
    closed: bool


def _visible_lines(weave: Weave) -> list[tuple[OpId | None, str]]:
    lines: list[tuple[OpId | None, str]] = []
    glyphs: list[str] = []
    first: OpId | None = None
    for strand in weave.strands:
        if strand.sheared:
            continue
        if strand.glyph == "\n":
            lines.append((first, "".join(glyphs)))
            glyphs = []
            first = None
            continue
        if first is None:
            first = strand.id
        glyphs.append(strand.glyph)
    lines.append((first, "".join(glyphs)))
    return lines


def fences(weave: Weave) -> list[Fence]:
    lines = _visible_lines(weave)
    result: list[Fence] = []
    index = 0
    total = len(lines)
    while index < total:
        pin, text = lines[index]
        opening = OPEN.match(text.strip())
        if opening is None or pin is None:
            index += 1
            continue
        ticks = len(opening.group(1))
        language = opening.group(2).strip()
        body: list[str] = []
        cursor = index + 1
        closed = False
        close_line: int | None = None
        while cursor < total:
            closing = CLOSE.match(lines[cursor][1].strip())
            if closing is not None and len(closing.group(1)) >= ticks:
                closed = True
                close_line = cursor
                break
            body.append(lines[cursor][1])
            cursor += 1
        result.append(
            Fence(
                language=language,
                body="\n".join(body),
                start_pin=pin,
                open_line=index,
                close_line=close_line,
                closed=closed,
            )
        )
        index = cursor + 1 if closed else total
    return result


def code_lines(weave: Weave) -> set[int]:
    inside: set[int] = set()
    total = len(_visible_lines(weave))
    for fence in fences(weave):
        last = fence.close_line if fence.closed else total
        inside.update(range(fence.open_line + 1, last))
    return inside


def in_code(weave: Weave, line: int) -> bool:
    return line in code_lines(weave)


def languages(weave: Weave) -> list[str]:
    seen = []
    for fence in fences(weave):
        if fence.language and fence.language not in seen:
            seen.append(fence.language)
    return seen


def report(weave: Weave) -> str:
    found = fences(weave)
    if not found:
        return "no code fences; the document is all prose"
    unclosed = sum(1 for fence in found if not fence.closed)
    tongues = ", ".join(languages(weave)) or "none named"
    return (
        f"{len(found)} fence(s), {unclosed} unclosed; "
        f"languages: {tongues}"
    )
