"""Legal outline: number a heading tree the academic way, roman then letter then digit.

Where the section-numbers module uses dotted decimals, formal
outlines cycle through styles by depth: upper roman for the top
level, upper letters for the next, decimals below that, then
lower letters, then lower roman, the sequence law reviews and
term papers use. This computes that label for each heading from
its depth and its position among its siblings, reusing the
roman module for the roman levels and a spreadsheet-style
letter converter for the letter levels, the one that counts A
through Z and then AA, so a section with twenty-seven children
labels the twenty-seventh AA rather than running out of
letters. The per-level counters reset the way an outline
expects: a new heading clears the counters of every level
deeper than it, so the first subsection under each section
starts again at A rather than continuing the previous section's
count, which is the behaviour that makes an outline readable
and no flat numbering gives. Beyond the five styles the cycle
repeats, upper roman again at the sixth level, because an
outline that deep is rare and repeating is more predictable
than inventing a sixth style few readers would recognize. It
renders the labels indented by depth beside their titles, a
view, and numbers nothing into the document, since writing
these labels in is the same operation the decimal numberer
already offers and duplicating it here would be two tools for
one job.
"""

from __future__ import annotations

from loom.headings import headings
from loom.romans import to_roman
from loom.weave import Weave

STYLES = (
    "upper-roman",
    "upper-letter",
    "decimal",
    "lower-letter",
    "lower-roman",
)


def _letters(number: int, upper: bool) -> str:
    base = 65 if upper else 97
    out = ""
    while number > 0:
        number, remainder = divmod(number - 1, 26)
        out = chr(base + remainder) + out
    return out


def label_for(level: int, ordinal: int) -> str:
    style = STYLES[(level - 1) % len(STYLES)]
    if style == "upper-roman":
        return to_roman(ordinal)
    if style == "lower-roman":
        return to_roman(ordinal).lower()
    if style == "upper-letter":
        return _letters(ordinal, upper=True)
    if style == "lower-letter":
        return _letters(ordinal, upper=False)
    return str(ordinal)


def outline_labels(weave: Weave) -> list[tuple[str, str]]:
    counters: dict[int, int] = {}
    result = []
    for heading in headings(weave):
        for deeper in [d for d in counters if d > heading.level]:
            del counters[deeper]
        counters[heading.level] = counters.get(heading.level, 0) + 1
        result.append(
            (heading.title, label_for(heading.level, counters[heading.level]))
        )
    return result


def render(weave: Weave) -> str:
    labels = outline_labels(weave)
    if not labels:
        return "no headings to outline"
    lines = []
    for (title, label), heading in zip(
        labels, headings(weave), strict=True
    ):
        indent = "  " * (heading.level - 1)
        lines.append(f"{indent}{label}. {title}")
    return "\n".join(lines)
