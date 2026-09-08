"""The basket: a shared set where adding wins and removal needs receipts.

Sets break in collaboration when remove means remove the
word: one hand removes the tag urgent while another,
unaware, re-adds it, and a word-level remove eats the
re-add it never saw. The basket removes by receipt
instead. Every add carries a dot, its operation id, an
item is present while any of its dots stands, and a pluck
names the exact dots it observed, so the concurrent
re-add, carrying a dot the plucker never saw, survives on
purpose, adding winning the way shared intentions should.
Dots arriving after their own pluck find themselves
already plucked, the basket remembering removals the way
the weave remembers its dead, which makes every arrival
order tell the same basket. What this refuses to be is a
counter: adding twice is two dots and one item, presence
being a fact and not a tally, and the census says both
numbers so nobody mistakes one for the other.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid
from loom.ids import OpId


@dataclass(frozen=True)
class Sprig:
    dot: OpId
    item: str

    def __post_init__(self) -> None:
        if not self.item.strip():
            raise Invalid(
                "a blank item is a basket holding air"
            )


@dataclass(frozen=True)
class Pluck:
    id: OpId
    dots: frozenset[OpId]


@dataclass
class Basket:
    sprigs: dict[OpId, str] = field(
        default_factory=dict
    )
    plucked: set[OpId] = field(default_factory=set)
    plucks_seen: set[OpId] = field(default_factory=set)

    def add(self, sprig: Sprig) -> str:
        if sprig.dot in self.plucked:
            return (
                f"{sprig.item!r} arrives already "
                "plucked; the basket remembers "
                "removals the way the weave "
                "remembers its dead"
            )
        if sprig.dot in self.sprigs:
            return (
                f"{sprig.dot.wire()} already in the "
                "basket; one dot, one sprig"
            )
        self.sprigs[sprig.dot] = sprig.item
        return (
            f"{sprig.item!r} added under "
            f"{sprig.dot.wire()}"
        )

    def dots_of(self, item: str) -> frozenset[OpId]:
        return frozenset(
            dot
            for dot, held in self.sprigs.items()
            if held == item and dot not in self.plucked
        )

    def pluck(self, pluck: Pluck) -> str:
        if pluck.id in self.plucks_seen:
            return (
                f"{pluck.id.wire()} already applied; "
                "one receipt, one removal"
            )
        self.plucks_seen.add(pluck.id)
        self.plucked |= pluck.dots
        return (
            f"{len(pluck.dots)} dot(s) plucked by "
            f"receipt; a re-add the plucker never "
            "saw survives on purpose"
        )

    def has(self, item: str) -> bool:
        return bool(self.dots_of(item))

    def items(self) -> list[str]:
        return sorted(
            {
                held
                for dot, held in self.sprigs.items()
                if dot not in self.plucked
            }
        )

    def census(self) -> str:
        standing = [
            dot
            for dot in self.sprigs
            if dot not in self.plucked
        ]
        return (
            f"{len(self.items())} item(s) on "
            f"{len(standing)} dot(s); presence is a "
            "fact, not a tally"
        )
