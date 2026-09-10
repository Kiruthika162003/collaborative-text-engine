"""Bellman-Ford: shortest paths that tolerate negative edges and expose a negative cycle.

Dijkstra finds shortest paths by settling the nearest unsettled
node and never revisiting it, which is fast and correct only while
every edge weight is non-negative, because settling relies on the
promise that no later, cheaper way into a node can appear once the
node is closed. A negative edge breaks that promise: a path that
looked longer can turn out shorter after descending through a
negative edge, arriving at an already-settled node by a cheaper
route Dijkstra will never reconsider. I had guessed Dijkstra would
cope with a few negative edges if they were small; it does not, it
returns a wrong distance without complaint, which is the dangerous
kind of wrong. Bellman-Ford gives up the greedy settling and
instead relaxes every edge, checking whether going through it
shortens the distance to its far end, and repeats that sweep over
all edges as many times as there are nodes less one. That many
sweeps suffice because a shortest path visits each node at most
once and so has at most that many edges, and each sweep is
guaranteed to extend every shortest path by at least one more edge,
so after enough sweeps every shortest path is fully found. It is
slower than Dijkstra, the node count times the edge count rather
than near-linear, and that is the price of correctness with
negative edges. The method also answers a question Dijkstra cannot
even pose: whether the graph has a negative cycle, a loop whose
weights sum below zero, around which a path could circle forever
getting cheaper so that no shortest distance exists. One extra
sweep after the others detects it, because if any edge still
shortens a distance when no shortest path can be longer than the
sweeps already allowed, that improvement can only come from a cycle
that keeps paying out, and this reports that rather than returning
distances that are quietly meaningless.
"""

from __future__ import annotations

import math

from loom.errors import Invalid


def bellman_ford(nodes: list, edges: list, source: object) -> tuple[dict, dict]:
    distance = dict.fromkeys(nodes, math.inf)
    predecessor: dict = dict.fromkeys(nodes)
    distance[source] = 0
    for _ in range(len(nodes) - 1):
        changed = False
        for tail, head, weight in edges:
            if distance[tail] + weight < distance[head]:
                distance[head] = distance[tail] + weight
                predecessor[head] = tail
                changed = True
        if not changed:
            break
    for tail, head, weight in edges:
        if distance[tail] + weight < distance[head]:
            raise Invalid("a negative cycle makes shortest distances undefined")
    return distance, predecessor


def has_negative_cycle(nodes: list, edges: list, source: object) -> bool:
    try:
        bellman_ford(nodes, edges, source)
    except Invalid:
        return True
    return False


def reconstruct_path(predecessor: dict, source: object, target: object) -> list | None:
    if target not in predecessor:
        return None
    path = [target]
    node = predecessor[target]
    while node is not None:
        path.append(node)
        node = predecessor[node]
    path.reverse()
    if path[0] != source:
        return None
    return path
