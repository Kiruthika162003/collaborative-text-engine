"""Union-find: track which items belong to the same group as merges accumulate.

Union-find is the structure for the equivalence question, are
these two items in the same group, when the groups form by
merging pairs over time, which is how connectivity in a graph
and clustering by relation both work. Each item points at a
representative, and two items are in the same group when they
reach the same representative; union merges two groups by
pointing one representative at the other. The two optimizations
that make it fast are both here. Path compression flattens the
chain to the representative every time find walks it, so
repeated queries on the same items get quicker, and union by
rank always hangs the shorter tree under the taller so the
trees stay shallow, which together make the operations almost
constant time amortized, the near-flat curve that lets a
program merge and query millions of times without slowing.
Items are added on first mention, so a caller unions items
without declaring them first, and any hashable item works, an
integer, a string, a strand id, because the structure cares
only about identity. The groups can be read out as the members
under each representative, which is the clustering the merges
produced, sorted within each group for a stable listing. It
answers same-group in the amortized-constant time its
optimizations buy and does not answer the reverse, undoing a
union, because a union-find with rollback is a different and
heavier structure, and this is the fast forward-only one that
the common uses want.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UnionFind:
    parent: dict = field(default_factory=dict)
    rank: dict = field(default_factory=dict)

    def _ensure(self, item) -> None:
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0

    def find(self, item):
        self._ensure(item)
        root = item
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[item] != root:
            self.parent[item], item = root, self.parent[item]
        return root

    def union(self, left, right) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1

    def connected(self, left, right) -> bool:
        return self.find(left) == self.find(right)

    def groups(self) -> dict:
        clusters: dict = {}
        for item in self.parent:
            clusters.setdefault(self.find(item), []).append(item)
        return {root: sorted(members) for root, members in clusters.items()}

    def group_count(self) -> int:
        return len({self.find(item) for item in self.parent})
