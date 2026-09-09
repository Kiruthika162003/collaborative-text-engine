"""Repeats: the doubled word and the duplicated line, the typos a reader skips over.

Two errors slip past every writer because the eye reads what
it expects: the doubled word, the the that the brain
collapses to one, and the duplicated line, the paste that
landed twice. This finds both. A doubled word is two
identical words in a row, case folded so The the counts,
separated by whitespace alone, because that, that with a
comma between is two clauses, not a stutter, and the gap has
to be blank for the repeat to be real. A duplicated line is a
non-blank line identical to the one just above it, the copy
that got pasted an extra time, blank lines exempt because a
run of blank lines is spacing, not duplication. The honest
caveat is that the tool cannot read intent: had had is
correct English and this flags it, that that is sometimes
right and this flags it too, because distinguishing the
stutter from the construction needs a parser this does not
carry, so the flags are offered as things to look at, not
verdicts, and the module says so rather than deleting a word
it decided was a mistake. Each doubled word pins to the
strand of the redundant second word, so a reader who fixes
one finds the rest still marked where they are.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import pairwise

from loom.ids import OpId
from loom.weave import Weave

WORD = re.compile(r"[A-Za-z']+")


@dataclass(frozen=True)
class Repeat:
    word: str
    pin: OpId
    position: int


def _visible_ids(weave: Weave) -> list[OpId]:
    return [
        strand.id for strand in weave.strands if not strand.sheared
    ]


def doubled_words(weave: Weave) -> list[Repeat]:
    text = weave.text()
    ids = _visible_ids(weave)
    matches = list(WORD.finditer(text))
    found = []
    for prev, cur in pairwise(matches):
        gap = text[prev.end() : cur.start()]
        if (
            prev.group().lower() == cur.group().lower()
            and gap != ""
            and gap.strip() == ""
        ):
            found.append(
                Repeat(
                    word=cur.group(),
                    pin=ids[cur.start()],
                    position=cur.start(),
                )
            )
    return found


def duplicate_lines(weave: Weave) -> list[int]:
    lines = weave.text().split("\n")
    dups = []
    for number in range(1, len(lines)):
        if lines[number].strip() and lines[number] == lines[number - 1]:
            dups.append(number)
    return dups


def report(weave: Weave) -> str:
    doubles = doubled_words(weave)
    dup_lines = duplicate_lines(weave)
    if not doubles and not dup_lines:
        return "no repeats found; nothing to look at"
    lines = []
    if doubles:
        words = ", ".join(sorted({repeat.word.lower() for repeat in doubles}))
        lines.append(f"{len(doubles)} doubled word(s): {words}")
    if dup_lines:
        lines.append(
            f"{len(dup_lines)} duplicated line(s) at "
            + ", ".join(str(number) for number in dup_lines)
        )
    lines.append(
        "flags to look at, not verdicts; had had is correct English"
    )
    return "\n".join(lines)
