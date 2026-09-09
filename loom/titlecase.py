"""Title case: capitalize a title the way a style guide does, small words and all.

Naive title case capitalizes every word, which gives The Lord
Of The Rings instead of The Lord of the Rings, so this follows
the rule a style guide actually uses: capitalize the words
that carry meaning and leave the small function words, the
articles and short conjunctions and prepositions, in lower
case, except the first and last word of the title, which are
always capitalized however small. Capitalizing a word means
raising its first letter and leaving the rest as typed, not
lowercasing the tail, so an acronym like NASA and a
deliberate inner capital like iPhone survive rather than
being flattened to Nasa and Iphone, which a title caser that
forced the whole word to one case would destroy. The rule is
one of several, and the module says so: AP and Chicago
disagree about which prepositions stay small and about the
length cutoff, and this picks one common list rather than
claiming a universal answer, so a house that follows a
different guide adjusts the list rather than fighting a
hidden one. Applied to a heading, it capitalizes the title
and leaves the hash marks alone, because the markers are
structure and only the words are the title. The whitespace
between words is normalized to single spaces in the process,
which is right for a title and named so a caller is not
surprised.
"""

from __future__ import annotations

import re

from loom.author import Author
from loom.linewise import lines_of
from loom.patch import patch
from loom.weave import Op

HEADING = re.compile(r"^(#{1,6}\s+)(.*)$")
SMALL_WORDS = frozenset(
    {
        "a", "an", "the", "and", "but", "or", "nor", "for", "yet", "so",
        "at", "by", "in", "of", "on", "to", "up", "as", "per", "via",
        "off", "out", "from", "into", "with", "over",
    }
)


def _capitalize(word: str) -> str:
    return word[:1].upper() + word[1:]


def title_case(text: str) -> str:
    words = text.split()
    if not words:
        return text
    result = []
    last = len(words) - 1
    for index, word in enumerate(words):
        edge = index in (0, last)
        if not edge and word.lower() in SMALL_WORDS:
            result.append(word.lower())
        else:
            result.append(_capitalize(word))
    return " ".join(result)


def retitle(author: Author, line: int) -> list[Op]:
    lines = lines_of(author.weave)
    text = lines[line]
    match = HEADING.match(text)
    if match is not None:
        rebuilt = match.group(1) + title_case(match.group(2))
    else:
        rebuilt = title_case(text)
    lines[line] = rebuilt
    return patch(author, "\n".join(lines))
