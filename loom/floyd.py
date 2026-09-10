"""Floyd-Warshall: shortest paths between every pair, built up one allowed stop at a time.

Where Dijkstra and Bellman-Ford each find shortest paths from one
source, Floyd-Warshall finds them between all pairs at once, filling
a table whose entry for a pair is the shortest distance from the
first to the second. It rests on one simple idea applied
relentlessly. Consider the shortest path from a node to another that
is allowed to pass only through some set of intermediate nodes;
allow one more node into that set, and the new shortest path is
either the old one, which did not need the new node, or it goes from
the start into the newly allowed node and then out of it to the end,
using the best paths to and from that node that the smaller set
already gave. So the whole table is built by considering each node
in turn as a newly permitted stop and, for every pair, asking
whether routing through that stop beats what was found before. Three
nested loops over the nodes, the outer one the node being permitted
and the inner two the pair being updated, fill the entire table in
time cubic in the node count and, notably, independent of how many
edges there are. I had guessed all-pairs shortest paths just meant
running a single-source algorithm from every node; that does work
and is actually faster on a sparse graph with few edges, but
Floyd-Warshall wins on a dense graph and is markedly simpler to get
right, being three loops and one comparison with none of the
priority queues or repeated sweeps the single-source methods need.
The order of the loops is the one place it is easy to go wrong, the
permitted-stop loop has to be outermost so that when a pair is
updated the paths through the current stop are already final, and
getting that order backwards silently computes something that is not
the shortest path. Like Bellman-Ford it tolerates negative edges and
can spot a negative cycle, which shows up here as a node whose
shortest distance to itself has dropped below zero, and it reports
that rather than hand back a table the cycle has made meaningless.
"""

from __future__ import annotations

import math

from loom.errors import Invalid


def floyd_warshall(nodes: list, edges: list) -> tuple[dict, dict]:
    distance = {
        tail: {head: (0 if tail == head else math.inf) for head in nodes} for tail in nodes
    }
    hop: dict = {tail: dict.fromkeys(nodes) for tail in nodes}
    for tail, head, weight in edges:
        if weight < distance[tail][head]:
            distance[tail][head] = weight
            hop[tail][head] = head
    for stop in nodes:
        for tail in nodes:
            through = distance[tail][stop]
            if through == math.inf:
                continue
            for head in nodes:
                candidate = through + distance[stop][head]
                if candidate < distance[tail][head]:
                    distance[tail][head] = candidate
                    hop[tail][head] = hop[tail][stop]
    for node in nodes:
        if distance[node][node] < 0:
            raise Invalid("a negative cycle makes shortest distances undefined")
    return distance, hop


def reconstruct_path(hop: dict, source: object, target: object) -> list | None:
    if source == target:
        return [source]
    if hop[source][target] is None:
        return None
    path = [source]
    node = source
    while node != target:
        node = hop[node][target]
        if node is None:
            return None
        path.append(node)
    return path
