"""The weave: a sequence CRDT where every replica arrives at the same cloth.

Each glyph is a strand: an id, the id of the strand it was
typed after, the character, and a rank. Insertion is the
whole algorithm. A strand enters after its origin, walks
right past anything attached deeper, and among true
siblings the higher rank stands closer, sites breaking
rank ties. The rank is a Lamport stamp and it exists
because of a measured failure, not a foresight: the first
design ordered siblings by the per-site counter, and the
duet trial promptly produced the foxbrown, Bob's insertion
losing to a resident run because his counter said one
while his eyes had seen thirteen. Delivery counters count
a site's own operations and must stay contiguous for the
clock; ordering needs a number that grows with everything
a site has witnessed, and those are two jobs no single
integer does honestly. Deletion shears rather than
removes, the tombstone staying to anchor late arrivals,
and apply is idempotent, the same operation twice weaving
once, since a network that never duplicates is a network
in a diagram.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid, Missing
from loom.ids import OpId

HEAD = None


@dataclass(frozen=True)
class Insert:
    id: OpId
    origin: OpId | None
    glyph: str
    rank: int

    def __post_init__(self) -> None:
        if len(self.glyph) != 1:
            raise Invalid(
                f"a strand carries one glyph, not "
                f"{len(self.glyph)}; runs are woven "
                "strand by strand so runs can merge "
                "strand by strand"
            )
        if self.rank < 1:
            raise Invalid(
                f"rank {self.rank} on {self.id.wire()}; "
                "ranks start at one and grow with "
                "everything a site has witnessed"
            )

    def seat_key(self) -> tuple[int, str]:
        return (self.rank, self.id.site)


@dataclass(frozen=True)
class Shear:
    id: OpId
    target: OpId


Op = Insert | Shear


@dataclass
class Strand:
    id: OpId
    origin: OpId | None
    glyph: str
    rank: int
    sheared: bool = False

    def seat_key(self) -> tuple[int, str]:
        return (self.rank, self.id.site)


@dataclass
class Weave:
    strands: list[Strand] = field(default_factory=list)
    by_id: dict[OpId, int] = field(default_factory=dict)
    shears_seen: set[OpId] = field(default_factory=set)

    def _position(self, op_id: OpId | None) -> int:
        if op_id is HEAD:
            return -1
        held = self.by_id.get(op_id)
        if held is None:
            raise Missing(
                f"{op_id.wire()} is not in the fabric; "
                "an origin unseen is usually an arrival "
                "out of order. Buffer it"
            )
        return held

    def _reindex(self, start: int) -> None:
        for index in range(start, len(self.strands)):
            self.by_id[self.strands[index].id] = index

    def _integrate(self, op: Insert) -> str:
        origin_pos = self._position(op.origin)
        pos = origin_pos + 1
        while pos < len(self.strands):
            standing = self.strands[pos]
            standing_origin = self._position(
                standing.origin
            )
            if standing_origin < origin_pos:
                break
            if (
                standing_origin == origin_pos
                and standing.seat_key() < op.seat_key()
            ):
                break
            pos += 1
        self.strands.insert(
            pos,
            Strand(
                id=op.id,
                origin=op.origin,
                glyph=op.glyph,
                rank=op.rank,
            ),
        )
        self._reindex(pos)
        return f"{op.id.wire()} woven at slot {pos}"

    def _shear(self, op: Shear) -> str:
        target_pos = self._position(op.target)
        strand = self.strands[target_pos]
        self.shears_seen.add(op.id)
        if strand.sheared:
            return (
                f"{op.target.wire()} was already "
                "sheared; two scissors, one cut"
            )
        strand.sheared = True
        return (
            f"{op.target.wire()} sheared; the "
            "tombstone stays to anchor late arrivals"
        )

    def apply(self, op: Op) -> str:
        if isinstance(op, Insert):
            if op.id in self.by_id:
                return (
                    f"{op.id.wire()} already woven; "
                    "the same operation twice weaves "
                    "once"
                )
            return self._integrate(op)
        if op.id in self.shears_seen:
            return (
                f"{op.id.wire()} already applied; the "
                "same operation twice weaves once"
            )
        return self._shear(op)

    def text(self) -> str:
        return "".join(
            strand.glyph
            for strand in self.strands
            if not strand.sheared
        )

    def visible_count(self) -> int:
        return sum(
            1
            for strand in self.strands
            if not strand.sheared
        )

    def tombstone_count(self) -> int:
        return sum(
            1
            for strand in self.strands
            if strand.sheared
        )

    def strand_at_visible(self, index: int) -> Strand:
        if index < 0:
            raise Invalid(
                "visible positions start at zero"
            )
        walked = -1
        for strand in self.strands:
            if strand.sheared:
                continue
            walked += 1
            if walked == index:
                return strand
        raise Missing(
            f"visible position {index} is past the "
            f"cloth; only {walked + 1} glyph(s) show"
        )

    def origin_for_insert_at(
        self, index: int
    ) -> OpId | None:
        """The strand a local insert at visible index should originate on."""
        if index < 0:
            raise Invalid(
                "visible positions start at zero"
            )
        if index == 0:
            return HEAD
        return self.strand_at_visible(index - 1).id
