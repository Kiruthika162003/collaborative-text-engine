"""SCC: the strongly connected components of a directed graph, by two depth-first passes.

In a directed graph a strongly connected component is a maximal
group of nodes where every node can reach every other, following
the arrows. Finding these groups looks like it should need
checking, for every pair of nodes, whether each can reach the
other, which is cubic. Kosaraju's method finds them all in two
linear depth-first passes instead. The first pass runs over the
graph and records the order in which nodes finish, that is, the
order in which the search exhausts everything reachable from them
and backs out; a node finishes after all the nodes it can reach,
so the finish order is a rough topological order that a cycle
merely ties. The second pass runs on the graph with every edge
reversed, taking nodes in reverse finish order, and each tree it
grows is exactly one component. That works because reversing the
edges keeps the components intact but cuts every one-way bridge
between them: within a component you can still get everywhere,
since mutual reachability survives reversal, but you can no longer
cross from one component into another the way the forward edges
let you, so a search on the reversed graph started from the
last-finished node stays trapped inside that node's component and
collects it whole. I had guessed carving out these groups needed
pairwise reachability, all-to-all; it needs two ordinary
traversals, because the finish order from the first pass tells the
second pass where to start so that each restart lands in a fresh
component, which is the surprising economy of it. The passes here
are iterative rather than recursive, keeping their own stack, so a
long chain of nodes cannot overflow the interpreter's call stack,
which a recursive depth-first search on a deep graph would. The
components come back each sorted and the whole list ordered by
smallest node, so the same graph always reports the same grouping,
since a decomposition that printed in traversal order would read
differently on graphs that were equal but built in a different
order.
"""

from __future__ import annotations


def _all_nodes(graph: dict) -> list:
    nodes = list(graph)
    seen = set(nodes)
    for neighbours in graph.values():
        for node in neighbours:
            if node not in seen:
                seen.add(node)
                nodes.append(node)
    return nodes


def _finish_order(graph: dict, nodes: list) -> list:
    visited: set = set()
    order: list = []
    for source in nodes:
        if source in visited:
            continue
        stack = [(source, iter(graph.get(source, ())))]
        visited.add(source)
        while stack:
            node, neighbours = stack[-1]
            advanced = False
            for neighbour in neighbours:
                if neighbour not in visited:
                    visited.add(neighbour)
                    stack.append((neighbour, iter(graph.get(neighbour, ()))))
                    advanced = True
                    break
            if not advanced:
                order.append(node)
                stack.pop()
    return order


def _transpose(graph: dict, nodes: list) -> dict:
    reversed_graph: dict = {node: [] for node in nodes}
    for node, neighbours in graph.items():
        for neighbour in neighbours:
            reversed_graph[neighbour].append(node)
    return reversed_graph


def strongly_connected_components(graph: dict) -> list:
    nodes = _all_nodes(graph)
    order = _finish_order(graph, nodes)
    reversed_graph = _transpose(graph, nodes)
    assigned: set = set()
    components: list = []
    for root in reversed(order):
        if root in assigned:
            continue
        stack = [root]
        assigned.add(root)
        component = []
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbour in reversed_graph.get(node, ()):
                if neighbour not in assigned:
                    assigned.add(neighbour)
                    stack.append(neighbour)
        components.append(sorted(component))
    components.sort(key=lambda group: group[0])
    return components


def is_strongly_connected(graph: dict) -> bool:
    components = strongly_connected_components(graph)
    return len(components) == 1
