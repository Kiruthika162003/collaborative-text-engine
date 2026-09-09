"""MST: the cheapest set of edges connecting every node, built greedily by Kruskal.

A minimum spanning tree of a weighted undirected graph is the
lightest collection of edges that still connects every node
together with no cycle, the cheapest possible wiring that leaves
nothing stranded. Kruskal builds it by pure greed and nothing
else: sort every edge by weight and consider them from cheapest to
dearest, taking an edge into the tree whenever its two endpoints
are not already connected and skipping it when they are, because
taking it would only close a cycle and add weight for no new
reach. Whether the two endpoints are already connected is exactly
the question a union-find structure answers quickly, so the whole
algorithm is a sort followed by a walk down the sorted edges
asking union-find one question each and merging when the answer is
no. I had guessed the cheapest tree would need trying combinations
of edges, some search with backtracking to undo a choice that
looked good early and boxed in a better one later; it does not, the
greedy choice is provably optimal with no backtracking at all. The
reason is the cut property: for any way of splitting the nodes into
two sides, the lightest edge crossing the split is in some minimum
spanning tree, and taking the next cheapest edge that does not form
a cycle is always taking the lightest edge across the cut that
separates what it would join from the rest, so every greedy pick is
a safe pick. That is the part that surprised me, that so simple a
rule needs no second-guessing, and it is why Kruskal is a sort plus
a union-find and not a search. If the graph is disconnected there
is no spanning tree at all, and the algorithm then yields a minimum
spanning forest, the cheapest wiring within each connected piece,
which shows up as fewer chosen edges than one less than the node
count, and this reports that honestly rather than pretending a
tree exists.
"""

from __future__ import annotations

from loom.unionfind import UnionFind


def minimum_spanning_tree(nodes: list, edges: list) -> tuple[list, object]:
    forest = UnionFind()
    for node in nodes:
        forest.find(node)
    chosen: list = []
    total = 0
    for weight, left, right in sorted(edges, key=lambda edge: edge[0]):
        if not forest.connected(left, right):
            forest.union(left, right)
            chosen.append((weight, left, right))
            total += weight
    return chosen, total


def is_spanning(nodes: list, chosen: list) -> bool:
    return len(chosen) == len(nodes) - 1
