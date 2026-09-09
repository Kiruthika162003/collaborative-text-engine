"""Ordered set: a set that remembers the order its members were added.

A plain set gives fast membership but forgets insertion order,
and sometimes a caller needs both, the deduplication of a set
and the order of a list, a list of things seen with duplicates
removed but the first sighting's position kept. This is that,
built on an insertion-ordered dictionary where the keys are the
members and the order they were inserted is the order they are
read back. Adding a member that is already present leaves its
original position rather than moving it to the end, because the
order that matters is when a member was first seen, not when it
was last mentioned, which is what makes this the right structure
for deduplicating a stream while preserving first appearance.
The set operations preserve order too, and preserve it from the
left operand: a union reads this set's members in their order
and then the other's members not already present, an
intersection reads this set's members that are also in the
other, and a difference reads this set's members not in the
other, so the result's order is always anchored to the set the
operation was called on. That left-anchoring is a choice, since
union is commutative as a set but not as an ordered one, and it
is stated so a caller who wants the other order calls the
operation on the other set. Membership and length are the
constant-time operations the underlying dict provides, so the
ordered set costs no more than a plain one for those and adds
only the order a list would have given, which is the trade that
makes it worth having over either alone.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OrderedSet:
    _members: dict = field(default_factory=dict)

    def add(self, member) -> OrderedSet:
        self._members.setdefault(member, None)
        return self

    def discard(self, member) -> OrderedSet:
        self._members.pop(member, None)
        return self

    def items(self) -> list:
        return list(self._members)

    def union(self, other: OrderedSet) -> OrderedSet:
        result = OrderedSet()
        for member in self._members:
            result.add(member)
        for member in other._members:
            result.add(member)
        return result

    def intersection(self, other: OrderedSet) -> OrderedSet:
        result = OrderedSet()
        for member in self._members:
            if member in other._members:
                result.add(member)
        return result

    def difference(self, other: OrderedSet) -> OrderedSet:
        result = OrderedSet()
        for member in self._members:
            if member not in other._members:
                result.add(member)
        return result

    def __contains__(self, member) -> bool:
        return member in self._members

    def __len__(self) -> int:
        return len(self._members)

    def __iter__(self):
        return iter(self._members)


def of(members: list) -> OrderedSet:
    result = OrderedSet()
    for member in members:
        result.add(member)
    return result
