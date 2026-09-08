"""Registers: single values shared by many hands, honest about ties.

A document is mostly its text, but never only: the title,
the language, the paper size, each a single value several
hands may set at once, and registers are how single values
converge. The last-writer register orders writes by
witness rank with sites breaking ties, the same order the
fabric already trusts, and later here means causally
later wherever causality exists, a write made after
seeing yours outranks yours everywhere. The every-voice
register refuses the pretense that ties have winners: two
writes at equal rank both stand, the reader receives every
standing value with its hand attached, and the tie
dissolves only under a write of higher rank, one made
having witnessed more, which is what settling a
disagreement actually means. The
choice between the two is editorial policy, not
correctness, and both are offered because a title can
afford a quiet winner while a legal clause cannot.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid


@dataclass(frozen=True)
class Write:
    site: str
    rank: int
    value: str

    def seat_key(self) -> tuple[int, str]:
        return (self.rank, self.site)


@dataclass
class LastWriter:
    standing: Write | None = None
    writes_seen: int = 0

    def write(self, entry: Write) -> str:
        self.writes_seen += 1
        if (
            self.standing is None
            or entry.seat_key()
            > self.standing.seat_key()
        ):
            self.standing = entry
            return (
                f"{entry.site} holds the pen; "
                f"{entry.value!r} stands"
            )
        return (
            f"{entry.site}'s write yields; "
            f"{self.standing.value!r} was written "
            "with more witnessed"
        )

    def read(self) -> str:
        if self.standing is None:
            raise Invalid(
                "an unwritten register has no value "
                "to pretend to"
            )
        return self.standing.value


@dataclass
class EveryVoice:
    standing: list[Write] = field(default_factory=list)

    def write(self, entry: Write) -> str:
        if any(
            held.site == entry.site
            and held.rank == entry.rank
            for held in self.standing
        ):
            return (
                f"{entry.site}:{entry.rank} already "
                "stands; one voice, one entry"
            )
        top = max(
            (held.rank for held in self.standing),
            default=0,
        )
        if entry.rank < top:
            return (
                f"{entry.value!r} arrives already "
                "dissolved; a voice that witnessed "
                "more is standing"
            )
        if entry.rank > top and self.standing:
            dissolved = len(self.standing)
            self.standing = [entry]
            return (
                f"{entry.value!r} stands and "
                f"dissolves {dissolved} earlier "
                "voice(s); settling means "
                "witnessing them all"
            )
        self.standing.append(entry)
        return (
            f"{entry.value!r} stands beside "
            f"{len(self.standing) - 1} other(s)"
        )

    def read(self) -> list[tuple[str, str]]:
        return sorted(
            (held.site, held.value)
            for held in self.standing
        )

    def settled(self) -> bool:
        return len(self.standing) == 1

    def page(self) -> str:
        if not self.standing:
            return "no voice has spoken"
        if self.settled():
            only = self.standing[0]
            return (
                f"settled: {only.value!r} by "
                f"{only.site}"
            )
        voices = "; ".join(
            f"{site} says {value!r}"
            for site, value in self.read()
        )
        return (
            f"{len(self.standing)} voices stand: "
            f"{voices}; ties have no winners here"
        )
