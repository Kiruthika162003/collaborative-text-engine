from __future__ import annotations

import math

import pytest

from loom.bellmanford import bellman_ford
from loom.errors import Invalid
from loom.floyd import floyd_warshall, reconstruct_path


class TestAllPairs:
    def test_a_small_graph(self):
        nodes = ["a", "b", "c", "d"]
        edges = [
            ("a", "b", 1),
            ("b", "c", 2),
            ("a", "c", 4),
            ("c", "d", 1),
        ]
        distance, _ = floyd_warshall(nodes, edges)
        assert distance["a"]["c"] == 3
        assert distance["a"]["d"] == 4
        assert distance["b"]["d"] == 3

    def test_the_diagonal_is_zero(self):
        nodes = [1, 2, 3]
        edges = [(1, 2, 5), (2, 3, 5)]
        distance, _ = floyd_warshall(nodes, edges)
        for node in nodes:
            assert distance[node][node] == 0

    def test_unreachable_pairs_stay_at_infinity(self):
        nodes = ["a", "b", "island"]
        edges = [("a", "b", 1)]
        distance, _ = floyd_warshall(nodes, edges)
        assert distance["a"]["island"] == math.inf

    def test_negative_edges_are_handled(self):
        nodes = [1, 2, 3]
        edges = [(1, 2, 4), (2, 3, -2), (1, 3, 5)]
        distance, _ = floyd_warshall(nodes, edges)
        assert distance[1][3] == 2


class TestPath:
    def test_reconstruct_a_route(self):
        nodes = ["a", "b", "c", "d"]
        edges = [("a", "b", 1), ("b", "c", 2), ("c", "d", 1)]
        _, hop = floyd_warshall(nodes, edges)
        assert reconstruct_path(hop, "a", "d") == ["a", "b", "c", "d"]

    def test_a_node_to_itself(self):
        nodes = ["a", "b"]
        edges = [("a", "b", 1)]
        _, hop = floyd_warshall(nodes, edges)
        assert reconstruct_path(hop, "a", "a") == ["a"]

    def test_no_route_between_islands(self):
        nodes = ["a", "b", "island"]
        edges = [("a", "b", 1)]
        _, hop = floyd_warshall(nodes, edges)
        assert reconstruct_path(hop, "a", "island") is None


class TestNegativeCycle:
    def test_detected(self):
        nodes = ["a", "b", "c"]
        edges = [("a", "b", 1), ("b", "c", -3), ("c", "a", 1)]
        with pytest.raises(Invalid):
            floyd_warshall(nodes, edges)


class TestAgreesWithBellmanFord:
    def test_the_two_agree_per_source(self):
        nodes = [1, 2, 3, 4, 5]
        edges = [
            (1, 2, 3),
            (1, 3, 8),
            (2, 4, 1),
            (3, 4, 2),
            (4, 5, 7),
            (2, 5, 4),
            (5, 3, -1),
        ]
        distance, _ = floyd_warshall(nodes, edges)
        for source in nodes:
            single, _ = bellman_ford(nodes, [(u, v, w) for u, v, w in edges], source)
            for target in nodes:
                assert distance[source][target] == single[target]
