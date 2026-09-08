"""Spellwatch: words checked against a given lexicon, flags pinned to the cloth.

Spellchecking a collaborative document is the same anchoring
problem wearing a dictionary: a squiggle under a misspelling
at offset forty is under the wrong word once anyone types
above it, so each flag pins to the strands of the word it
doubts and reports its position on demand. The lexicon is
injected, never bundled, because the loom does not own a
language and a checker that ships one language is wrong for
every document in another, and a caller with a medical
dictionary or a Welsh one deserves the same machinery. A
word is doubted when its lowercase form is absent from the
lexicon, and words with digits are skipped rather than
flagged, since a version string is not a spelling error and
a checker that reddens every identifier trains the writer
to ignore red. A flag whose word has been edited clears
itself, because the doubt was about specific letters and
those letters are gone, and a stale squiggle is worse than
none. The count of doubts is reported, never a score,
because spelling is checked and not graded.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from loom.ids import OpId
from loom.weave import Weave

WORD = re.compile(r"[A-Za-z]+")
TOKEN = re.compile(r"\S+")


@dataclass(frozen=True)
class Doubt:
    word: str
    first: OpId
    last: OpId
    at: int


@dataclass
class Spellwatch:
    lexicon: set = field(default_factory=set)

    def _visible(self, weave: Weave):
        return [
            strand
            for strand in weave.strands
            if not strand.sheared
        ]

    def doubts(self, weave: Weave) -> list[Doubt]:
        visible = self._visible(weave)
        cloth = "".join(s.glyph for s in visible)
        found: list[Doubt] = []
        for match in TOKEN.finditer(cloth):
            token = match.group()
            if any(ch.isdigit() for ch in token):
                continue
            letters = WORD.fullmatch(token.strip(".,!?;:"))
            if letters is None:
                continue
            word = letters.group()
            if word.lower() in self.lexicon:
                continue
            start = match.start() + token.index(word)
            end = start + len(word) - 1
            found.append(
                Doubt(
                    word=word,
                    first=visible[start].id,
                    last=visible[end].id,
                    at=start,
                )
            )
        return found

    def still_doubted(
        self, weave: Weave, doubt: Doubt
    ) -> bool:
        first = weave.by_id.get(doubt.first)
        last = weave.by_id.get(doubt.last)
        if first is None or last is None:
            return False
        stretch = "".join(
            strand.glyph
            for strand in weave.strands[first : last + 1]
            if not strand.sheared
        )
        return stretch == doubt.word

    def report(self, weave: Weave) -> str:
        found = self.doubts(weave)
        if not found:
            return (
                "no words doubted against this lexicon"
            )
        words = ", ".join(d.word for d in found)
        return (
            f"{len(found)} word(s) doubted: {words}; "
            "checked, not graded"
        )
