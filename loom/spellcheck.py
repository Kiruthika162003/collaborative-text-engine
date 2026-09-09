"""Spell check: spellwatch's doubts, minus the code, plus a suggestion for each.

Spellwatch flags words absent from a lexicon; this makes those
flags actionable by doing two things around them. It skips the
words inside fenced code blocks, borrowing the fences module
to know which lines are code, because a variable name or a
shell flag is not a misspelling and reddening it trains a
writer to ignore the red. And for each remaining doubt it
offers suggestions, the nearest lexicon words by edit distance
from the did-you-mean module, turning a bare this-is-wrong
into a here-is-what-you-probably-meant. The lexicon is still
the caller's, injected not bundled, the same discipline
spellwatch keeps, so this owns no language either; it only
arranges the three organs so a caller with a dictionary gets a
report they can act on line by line. It reports and does not
correct, because which suggestion is right is the writer's
call and an autocorrect that chose would eventually choose
wrong, changing a rare correct word into a common one. A
document with a lexicon that covers it produces an empty
report, and a word with no near neighbour in the lexicon is
still reported, just with no suggestion, because a misspelling
too far from any real word is still a misspelling worth
flagging even when the checker cannot guess the fix.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.didyoumean import nearest
from loom.fences import code_lines
from loom.linewise import line_of
from loom.spellwatch import Spellwatch
from loom.weave import Weave


@dataclass(frozen=True)
class Correction:
    word: str
    line: int
    suggestions: list[str]


def check(weave: Weave, lexicon: set[str]) -> list[Correction]:
    watch = Spellwatch(lexicon=lexicon)
    code = code_lines(weave)
    out = []
    for doubt in watch.doubts(weave):
        line = line_of(weave, doubt.first)
        if line in code:
            continue
        suggestions = [
            word for word, _distance in nearest(doubt.word.lower(), lexicon)
        ]
        out.append(
            Correction(word=doubt.word, line=line, suggestions=suggestions)
        )
    return out


def clean(weave: Weave, lexicon: set[str]) -> bool:
    return not check(weave, lexicon)


def report(weave: Weave, lexicon: set[str]) -> str:
    found = check(weave, lexicon)
    if not found:
        return "spelling clean against the given lexicon"
    lines = [f"{len(found)} doubtful word(s):"]
    for correction in found:
        tail = (
            "; did you mean " + ", ".join(correction.suggestions)
            if correction.suggestions
            else "; no near word in the lexicon"
        )
        lines.append(
            f"  line {correction.line}: {correction.word!r}{tail}"
        )
    return "\n".join(lines)
