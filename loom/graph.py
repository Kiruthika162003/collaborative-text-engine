"""Graph: a directed graph with topological ordering and cycle detection.

Dependencies form a directed graph, a task pointing at the
tasks it must follow, and the question they pose is an order to
do them in that respects every edge, which is a topological
sort. This holds the graph as each node's list of successors
and computes that order by Kahn's algorithm: count how many
edges point into each node, start with the nodes nothing points
at, and repeatedly take one, remove it, and reduce the in-count
of its successors, adding a successor to the ready set when its
last incoming edge is removed. The order it produces is
deterministic, because the ready set is kept sorted so ties
break the same way every run, which matters when a caller
compares two orderings or expects a stable build sequence. The
algorithm doubles as a cycle detector: a graph with a cycle has
no node with zero remaining in-edges once the cycle is all that
is left, so the process stops having emitted fewer nodes than
the graph holds, and that shortfall is exactly a cycle. A
topological sort of a cyclic graph is refused with that
diagnosis rather than returning a partial order, because a
partial order presented as complete would have a caller run
tasks before their dependencies. Adding an edge adds both its
endpoints, so a caller builds the graph by stating edges
without declaring nodes first, and a node nothing connects to
still appears in the order, since an isolated task is a task to
do, just one with no constraints on when.
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass, field

from loom.errors import Invalid


@dataclass
class Graph:
    edges: dict = field(default_factory=dict)

    def add_node(self, node) -> None:
        self.edges.setdefault(node, [])

    def add_edge(self, source, target) -> None:
        self.add_node(source)
        self.add_node(target)
        self.edges[source].append(target)

    def neighbors(self, node) -> list:
        return list(self.edges.get(node, []))

    def nodes(self) -> list:
        return sorted(self.edges)

    def topological_sort(self) -> list:
        indegree = dict.fromkeys(self.edges, 0)
        for source in self.edges:
            for target in self.edges[source]:
                indegree[target] += 1
        ready = sorted(node for node, count in indegree.items() if count == 0)
        order = []
        while ready:
            node = ready.pop(0)
            order.append(node)
            for target in self.edges[node]:
                indegree[target] -= 1
                if indegree[target] == 0:
                    bisect.insort(ready, target)
        if len(order) != len(indegree):
            raise Invalid("the graph has a cycle; no topological order exists")
        return order

    def has_cycle(self) -> bool:
        try:
            self.topological_sort()
        except Invalid:
            return True
        return False
