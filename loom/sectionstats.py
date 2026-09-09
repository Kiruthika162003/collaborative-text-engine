"""Section stats: the word count under each heading, so a writer finds the thin section.

A whole-document word count hides the section that ran thin,
the heading with two sentences under it where the others have
twenty, and a writer balancing a document wants exactly that
per-section figure. This walks the text, splitting it at the
headings the headings module recognizes and counting the words
of the body under each, so every section reports its own
weight. The text before the first heading is a section too,
the preamble, reported under its own name rather than folded
into the first heading's count where it does not belong, and
dropped when it is empty so a document that opens with a
heading is not prefixed by a phantom section of zero words.
The heading line's own words are not counted in its body,
because a heading is a label, not the section's prose, and
counting it would inflate a one-line section into looking
fuller than it reads. The threshold that marks a section thin
is the caller's, since thin for a reference entry is fat for a
footnote, and the counts are reported as the measurements they
are: a short section is sometimes short because it should be,
and no word count knows which, the same restraint the other
reading organs keep.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.headings import _parse_heading
from loom.weave import Weave

PREAMBLE = "(preamble)"


@dataclass(frozen=True)
class Section:
    title: str
    level: int
    words: int


def section_words(weave: Weave) -> list[Section]:
    result: list[Section] = []
    title = PREAMBLE
    level = 0
    words = 0
    for line in weave.text().split("\n"):
        parsed = _parse_heading(line)
        if parsed is not None:
            result.append(Section(title=title, level=level, words=words))
            level, title = parsed
            words = 0
        else:
            words += len(line.split())
    result.append(Section(title=title, level=level, words=words))
    if result and result[0].title == PREAMBLE and result[0].words == 0:
        result = result[1:]
    return result


def thin_sections(weave: Weave, threshold: int) -> list[Section]:
    return [
        section
        for section in section_words(weave)
        if section.words < threshold
    ]


def total_words(weave: Weave) -> int:
    return sum(section.words for section in section_words(weave))


def report(weave: Weave) -> str:
    sections = section_words(weave)
    if not sections:
        return "no sections; the document has no headings or body"
    lines = [f"{len(sections)} section(s):"]
    for section in sections:
        lines.append(f"  {section.title}: {section.words} word(s)")
    lines.append(
        "measurements, not verdicts; a short section is sometimes "
        "short because it should be"
    )
    return "\n".join(lines)
