"""The library: one hand, many documents, no operation crossing shelves.

A person edits more than one document, and the library is
the shelf discipline that keeps them from bleeding into
each other: every document is its own station with its own
weave, clock, and journal, opened by name, and an
operation belongs to exactly the document it was minted
in, the library refusing to hear into a document that does
not exist rather than helpfully creating it, because
auto-created documents are how typos become permanent
residents. Opening an already-open document hands back the
same station, opening being idempotent the way arriving
twice should be, and burning a document is loud and final,
the name quoted in the receipt. Library sync is pairwise
by shared name, each shared document shaking hands on its
own wire, and the unshared shelves are named at the end
rather than silently skipped, since the document only one
side has is exactly the one somebody thinks is shared.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Missing
from loom.handshake import shake
from loom.ids import check_site
from loom.prose import word_count
from loom.station import Station


@dataclass
class Library:
    site: str
    docs: dict[str, Station] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        check_site(self.site)

    def open_doc(self, name: str) -> Station:
        held = self.docs.get(name)
        if held is not None:
            return held
        station = Station.named(self.site)
        self.docs[name] = station
        return station

    def _existing(self, name: str) -> Station:
        held = self.docs.get(name)
        if held is None:
            raise Missing(
                f"{name!r} is not on these shelves; "
                "the catalogue holds "
                + (
                    ", ".join(
                        repr(title)
                        for title in sorted(self.docs)
                    )
                    or "nothing"
                )
                + ". Auto-creating would make typos "
                "permanent residents"
            )
        return held

    def type_in(
        self, name: str, index: int, text: str
    ):
        return self._existing(name).type_at(
            index, text
        )

    def hear_in(self, name: str, op) -> str:
        return self._existing(name).hear(op)

    def burn(self, name: str) -> str:
        self._existing(name)
        del self.docs[name]
        return (
            f"{name!r} burned; loud and final, the "
            "name quoted so nobody wonders"
        )

    def catalogue(self) -> str:
        if not self.docs:
            return (
                "empty shelves; every library starts "
                "this way"
            )
        lines = [
            f"{len(self.docs)} document(s) on "
            f"{self.site}'s shelves:"
        ]
        for name in sorted(self.docs):
            station = self.docs[name]
            lines.append(
                f"  {name}: "
                f"{word_count(station.author.weave)} "
                "word(s)"
            )
        return "\n".join(lines)


def sync_libraries(
    mine: Library, theirs: Library
) -> str:
    shared = sorted(
        set(mine.docs) & set(theirs.docs)
    )
    receipts = []
    for name in shared:
        receipts.append(
            f"{name}: "
            + shake(mine.docs[name], theirs.docs[name])
        )
    only_mine = sorted(
        set(mine.docs) - set(theirs.docs)
    )
    only_theirs = sorted(
        set(theirs.docs) - set(mine.docs)
    )
    for name in only_mine:
        receipts.append(
            f"{name}: only on {mine.site}'s "
            "shelves; the document one side has is "
            "exactly the one somebody thinks is "
            "shared"
        )
    for name in only_theirs:
        receipts.append(
            f"{name}: only on {theirs.site}'s shelves"
        )
    return "\n".join(receipts) or (
        "two empty libraries; nothing to reconcile"
    )
