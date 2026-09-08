"""The version vector: what each replica has seen, stated without modesty.

Wall clocks lie between machines, so the loom keeps time
the honest way: a vector of per-site counters, each entry
the highest contiguous counter this replica has woven from
that site. Contiguity is the load-bearing word. A vector
that records seeing operation 7 while 5 is still in the
post would promise causal delivery it cannot honor, so
observation refuses gaps: you observe 5, then 6, then 7,
and an arrival from the future is the caller's cue to
buffer, not the vector's job to forgive. Comparison gives
the three answers distributed time actually has, dominates,
dominated, or concurrent, and the merge takes the pointwise
maximum, which is correct exactly because each entry is a
statement about a prefix. The wire form sorts its sites so
two equal vectors render as equal strings, because a clock
that prints nondeterministically fails the first diff a
human ever runs on it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid, Stale, Torn
from loom.ids import OpId, check_site


@dataclass
class VersionVector:
    seen: dict[str, int] = field(default_factory=dict)

    def top(self, site: str) -> int:
        return self.seen.get(site, 0)

    def observe(self, op_id: OpId) -> str:
        expected = self.top(op_id.site) + 1
        if op_id.counter < expected:
            raise Stale(
                f"{op_id.wire()} was already woven; "
                f"{op_id.site} stands at "
                f"{self.top(op_id.site)}"
            )
        if op_id.counter > expected:
            raise Invalid(
                f"{op_id.wire()} arrives from the "
                f"future; {op_id.site} stands at "
                f"{self.top(op_id.site)} and gaps "
                "would promise causal delivery this "
                "vector cannot honor. Buffer it"
            )
        self.seen[op_id.site] = op_id.counter
        return f"{op_id.wire()} observed"

    def has(self, op_id: OpId) -> bool:
        return op_id.counter <= self.top(op_id.site)

    def dominates(self, other: VersionVector) -> bool:
        return all(
            self.top(site) >= counter
            for site, counter in other.seen.items()
        )

    def concurrent_with(
        self, other: VersionVector
    ) -> bool:
        return not self.dominates(other) and not (
            other.dominates(self)
        )

    def merge(self, other: VersionVector) -> str:
        grew = 0
        for site, counter in other.seen.items():
            check_site(site)
            if counter > self.top(site):
                self.seen[site] = counter
                grew += 1
        return (
            f"merged; {grew} site(s) advanced, the "
            "pointwise maximum being correct exactly "
            "because each entry is a statement about "
            "a prefix"
        )

    def copy(self) -> VersionVector:
        return VersionVector(seen=dict(self.seen))

    def wire(self) -> str:
        if not self.seen:
            return "@empty"
        return "@" + ",".join(
            f"{site}:{self.seen[site]}"
            for site in sorted(self.seen)
        )

    @classmethod
    def parse(cls, text: str) -> VersionVector:
        if not text.startswith("@"):
            raise Torn(
                f"{text!r} is not a vector; vectors "
                "open with @ so nobody mistakes one "
                "for an op id"
            )
        body = text[1:]
        if body == "empty":
            return cls()
        vector = cls()
        for part in body.split(","):
            op_id = OpId.parse(part)
            if vector.top(op_id.site):
                raise Torn(
                    f"{text!r} names "
                    f"{op_id.site} twice; a clock "
                    "with two opinions is not a clock"
                )
            vector.seen[op_id.site] = op_id.counter
        return vector
