"""Prose numbers: what writers actually ask the page, answered plainly.

Engines count strands; writers count words, and this
module answers the writer's questions without borrowing
anyone's definition of readability: words are maximal runs
of non-space glyphs, lines are what newlines make, the
longest word is named because it is usually a bug or a
URL, and the average word length is given to one decimal
because integers flatter and false precision preens. The
counts run on the visible cloth only, the writer's page
being the living one, and the empty page returns zeros
without ceremony since every draft starts there. One
number is refused on principle: this module will not score
readability, grade level, or sentiment, because a number
that claims to measure prose quality is an opinion wearing
a lab coat, and the loom does not dress opinions.
"""

from __future__ import annotations

from loom.weave import Weave


def words_of(weave: Weave) -> list[str]:
    return weave.text().split()


def word_count(weave: Weave) -> int:
    return len(words_of(weave))


def longest_word(weave: Weave) -> str:
    held = words_of(weave)
    if not held:
        return ""
    return max(held, key=lambda word: (len(word), word))


def average_word_length(weave: Weave) -> float:
    held = words_of(weave)
    if not held:
        return 0.0
    return sum(len(word) for word in held) / len(held)


def page(weave: Weave) -> str:
    held = words_of(weave)
    if not held:
        return (
            "0 words; every draft starts here, no "
            "ceremony required"
        )
    lines = weave.text().split("\n")
    champion = longest_word(weave)
    report = [
        f"{len(held)} word(s) on {len(lines)} "
        f"line(s), {weave.visible_count()} glyph(s)",
        f"longest word {champion!r} at "
        f"{len(champion)}; usually a bug or a URL",
        f"average word length "
        f"{average_word_length(weave):.1f}; one "
        "decimal, because integers flatter and "
        "false precision preens",
        "no readability score on principle; a "
        "number that grades prose is an opinion "
        "wearing a lab coat",
    ]
    return "\n".join(report)
