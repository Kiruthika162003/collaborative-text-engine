"""The circle: every author wired to every other, and one hard question.

A circle seats N authors and strings a link from each to
each, all sharing a temperament and a seed family, then
gives trials the two verbs they repeat forever: say, which
broadcasts an author's freshly minted operations onto all
their outgoing links, and settle, which delivers batches
around the ring until a full lap moves nothing, the
distributed editing equivalent of waiting for the dust.
The hard question comes after the dust: converged asks
every author for their text and refuses to summarize
disagreement, raising Diverged with every differing
reading quoted, because the one error this codebase never
converts to a return value is the one that means the
product is broken. When the texts agree the circle
answers with the text itself, singular, which is the
entire point of the loom said as a return type.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.author import Author
from loom.courier import Link
from loom.errors import Diverged, Invalid, Missing
from loom.mailroom import Mailroom
from loom.weave import Op


@dataclass
class Circle:
    authors: dict[str, Author] = field(
        default_factory=dict
    )
    mailrooms: dict[str, Mailroom] = field(
        default_factory=dict
    )
    links: dict[tuple[str, str], Link] = field(
        default_factory=dict
    )

    @classmethod
    def of(
        cls,
        sites: list[str],
        temperament: str = "calm",
        seed: int = 0,
    ) -> Circle:
        if len(sites) < 2:
            raise Invalid(
                "a circle of one is a diary; seat at "
                "least two"
            )
        circle = cls()
        for site in sites:
            author = Author(site=site)
            circle.authors[site] = author
            circle.mailrooms[site] = Mailroom(
                author=author
            )
        for source in sites:
            for target in sites:
                if source == target:
                    continue
                circle.links[(source, target)] = Link(
                    to=circle.mailrooms[target],
                    temperament=temperament,
                    seed=seed
                    + len(circle.links) * 7919,
                )
        return circle

    def author(self, site: str) -> Author:
        held = self.authors.get(site)
        if held is None:
            raise Missing(
                f"{site} is not seated at this circle"
            )
        return held

    def say(self, site: str, ops: list[Op]) -> str:
        self.author(site)
        for (source, _target), link in (
            self.links.items()
        ):
            if source == site:
                link.post_many(ops)
        return (
            f"{site} says {len(ops)} operation(s) to "
            f"{len(self.authors) - 1} listener(s)"
        )

    def settle(self) -> str:
        laps = 0
        moved = True
        while moved:
            moved = False
            laps += 1
            for link in self.links.values():
                if link.deliver_batch():
                    moved = True
        shelved = sum(
            len(room.shelf)
            for room in self.mailrooms.values()
        )
        return (
            f"settled after {laps} lap(s); "
            f"{shelved} arrival(s) still shelved"
        )

    def converged(self) -> str:
        readings = {
            site: author.text()
            for site, author in self.authors.items()
        }
        distinct = sorted(set(readings.values()))
        if len(distinct) > 1:
            quoted = "; ".join(
                f"{site} reads {text!r}"
                for site, text in sorted(
                    readings.items()
                )
            )
            raise Diverged(
                f"{len(distinct)} different readings "
                f"where one was promised: {quoted}"
            )
        return distinct[0]

    def mischief_bill(self) -> str:
        posted = sum(
            link.posted for link in self.links.values()
        )
        duplicated = sum(
            link.duplicated
            for link in self.links.values()
        )
        return (
            f"{len(self.links)} link(s), {posted} "
            f"posting(s), {duplicated} duplicate(s) "
            "manufactured"
        )
