"""Dijkstra: shortest paths from a source in a weighted graph with non-negative edges.

Dijkstra's algorithm finds the least-cost path from a start
node to every other, and this implements it on the min-heap:
it keeps the best known distance to each node, and repeatedly
takes the unfinished node with the smallest known distance,
which the heap surfaces, and relaxes its edges, lowering a
neighbour's distance when going through this node is cheaper.
The heap is what makes it efficient, giving the next closest
node in logarithmic time rather than a scan, and a stale heap
entry, one whose distance a later relaxation improved on, is
skipped when it surfaces because its distance no longer matches
the best known, which is the standard way to use a heap that
cannot decrease a key in place. The one hard requirement is
stated because violating it silently gives wrong answers:
edge weights must be non-negative, since Dijkstra's greedy
choice, that the closest unfinished node is final, holds only
when no negative edge could later undercut it; a graph with a
negative edge needs Bellman-Ford, not this. Nodes the start
cannot reach simply do not appear in the result, rather than
appearing with an infinite distance, because a missing key is
the honest way to say unreachable and a caller checks for it.
The distances are the costs of the cheapest paths, not the
paths themselves; a caller who needs the route as well keeps a
predecessor map, which this leaves out to stay the focused
shortest-distance computation the common case asks for.
"""

from __future__ import annotations

import math

from loom.heap import MinHeap


def shortest_paths(graph: dict, start) -> dict:
    distance = {start: 0}
    heap = MinHeap()
    heap.push((0, start))
    while len(heap):
        current, node = heap.pop()
        if current > distance.get(node, math.inf):
            continue
        for neighbour, weight in graph.get(node, []):
            candidate = current + weight
            if candidate < distance.get(neighbour, math.inf):
                distance[neighbour] = candidate
                heap.push((candidate, neighbour))
    return distance


def shortest_distance(graph: dict, start, end) -> float | None:
    return shortest_paths(graph, start).get(end)
