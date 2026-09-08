"""Citations: numbered references that count sources, not marks.

A footnote numbers every mark in the text; a citation
numbers distinct sources and reuses a number when the same
source is cited again, so the third reference to Smith is
still [1] and the works-cited list holds one Smith, not
three. That is the difference this module carries over the
apparatus: the numbering is keyed by source in first
appearance order, walking the text once, handing each new
key the next number and every repeat the number it already
earned. Each citation pins to the strand it follows, so its
place in the reading order moves as the document grows and
the numbering recomputes rather than being stored, the same
anchor discipline the footnotes keep. The sources live in a
shared bibliography keyed by a short cite-key, and merging
two authors' bibliographies unions them by key, but two
people defining the same key as two different papers is a
real disagreement, not a merge, so it is raised rather than
resolved by a coin toss, because a silent pick would print
one author's Smith under the other's number and cite the
wrong paper in a voice that sounds certain. A citation of a
key the bibliography does not hold is refused, since a
number pointing at no source is worse than no number.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Diverged, Invalid, Missing
from loom.ids import OpId
from loom.weave import Weave


@dataclass(frozen=True)
class Source:
    key: str
    author: str
    title: str
    year: int | None = None

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise Invalid("a source needs a cite-key to be cited by")
        if not self.author.strip() and not self.title.strip():
            raise Invalid(
                "a source with neither author nor title is a "
                "reference to nothing"
            )

    def reference(self) -> str:
        head = self.author.strip() or "Anon"
        tail = self.title.strip() or "untitled"
        if self.year is not None:
            return f"{head} ({self.year}). {tail}."
        return f"{head}. {tail}."


@dataclass
class Bibliography:
    sources: dict[str, Source] = field(default_factory=dict)

    def enter(self, source: Source) -> str:
        existing = self.sources.get(source.key)
        if existing is not None and existing != source:
            raise Diverged(
                f"key {source.key!r} already names a different "
                "source; two papers under one key is a "
                "disagreement, not a merge"
            )
        self.sources[source.key] = source
        return f"source {source.key!r} entered"

    def has(self, key: str) -> bool:
        return key in self.sources

    def merge(self, other: Bibliography) -> Bibliography:
        merged = Bibliography(dict(self.sources))
        for source in other.sources.values():
            merged.enter(source)
        return merged


@dataclass(frozen=True)
class Citation:
    id: OpId
    anchor: OpId
    key: str


@dataclass
class Citations:
    weave: Weave
    bibliography: Bibliography
    marks: dict[OpId, Citation] = field(default_factory=dict)

    def cite(self, citation: Citation) -> str:
        if citation.anchor not in self.weave.by_id:
            raise Missing(
                f"{citation.anchor.wire()} is not in the text; "
                "a citation needs a point to follow. Buffer it"
            )
        if not self.bibliography.has(citation.key):
            raise Missing(
                f"key {citation.key!r} is not in the "
                "bibliography; a number pointing at no source "
                "is worse than no number"
            )
        self.marks[citation.id] = citation
        return f"cited {citation.key!r} at {citation.anchor.wire()}"

    def _live(self) -> list[Citation]:
        live = []
        for citation in self.marks.values():
            pos = self.weave.by_id.get(citation.anchor)
            if pos is not None and not self.weave.strands[pos].sheared:
                live.append(citation)
        return sorted(
            live, key=lambda c: self.weave.by_id[c.anchor]
        )

    def order(self) -> list[str]:
        seen: list[str] = []
        for citation in self._live():
            if citation.key not in seen:
                seen.append(citation.key)
        return seen

    def numbering(self) -> dict[str, int]:
        return {
            key: number
            for number, key in enumerate(self.order(), start=1)
        }

    def in_text(self) -> list[int]:
        numbers = self.numbering()
        return [numbers[c.key] for c in self._live()]

    def works_cited(self) -> str:
        order = self.order()
        if not order:
            return "no citations"
        lines = []
        for number, key in enumerate(order, start=1):
            source = self.bibliography.sources[key]
            lines.append(f"[{number}] {source.reference()}")
        return "\n".join(lines)
