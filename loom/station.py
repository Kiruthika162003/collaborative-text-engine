"""The station: one participant, fully equipped, nothing reaching around.

A station is what a real deployment would run per person:
the author for gestures, the mailroom for arrivals, the
journal for memory, wired so every operation that exists
here is journaled here, whether the station minted it or
heard it. Gestures journal their own operations before
returning them for whatever transport the caller runs;
hearing journals first and weaves second, because an
operation on the shelf is still an operation this station
must be able to re-send, and a journal that only remembers
the woven forgets exactly the operations a crashed peer
will ask about. The station answers the sync question from
its own journal and its own clock and nothing else, which
is the property that makes stations composable: two of
them, a wire of any quality between, and the handshake has
everything it needs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.author import Author
from loom.clock import VersionVector
from loom.journal import Journal
from loom.mailroom import Mailroom
from loom.weave import Op


@dataclass
class Station:
    author: Author
    mailroom: Mailroom
    journal: Journal = field(default_factory=Journal)

    @classmethod
    def named(cls, site: str) -> Station:
        author = Author(site=site)
        return cls(
            author=author,
            mailroom=Mailroom(author=author),
        )

    @property
    def site(self) -> str:
        return self.author.site

    def text(self) -> str:
        return self.author.text()

    def clock(self) -> VersionVector:
        return self.author.clock

    def type_at(
        self, index: int, text: str
    ) -> list[Op]:
        ops = self.author.type_at(index, text)
        for op in ops:
            self.journal.record(op)
        return ops

    def erase_at(
        self, index: int, count: int
    ) -> list[Op]:
        ops = self.author.erase_at(index, count)
        for op in ops:
            self.journal.record(op)
        return ops

    def hear(self, op: Op) -> str:
        self.journal.record(op)
        return self.mailroom.receive(op)

    def ops_missing_for(
        self, clock: VersionVector
    ) -> list[Op]:
        return self.journal.missing_for(clock)
