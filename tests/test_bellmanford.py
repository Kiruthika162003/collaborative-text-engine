from __future__ import annotations

import math

import pytest

from loom.bellmanford import bellman_ford, has_negative_cycle, reconstruct_path
from loom.errors import Invalid


class TestDistances:
    def test_a_simple_positive_graph(self):
        nodes = ["a", "b", "c", "d"]
        edges = [
            ("a", "b", 1),
            ("b", "c", 2),
            ("a", "c", 4),
            ("c", "d", 1),
        ]
        distance, _ = bellman_ford(nodes, edges, "a")
        assert distance["c"] == 3
        assert distance["d"] == 4

    def test_negative_edges_are_handled(self):
        nodes = [1, 2, 3, 4]
        edges = [
            (1, 2, 4),
            (1, 3, 5),
            (2, 3, -3),
            (3, 4, 2),
        ]
        distance, _ = bellman_ford(nodes, edges, 1)
        assert distance[3] == 1
        assert distance[4] == 3

    def test_an_unreachable_node_stays_at_infinity(self):
        nodes = ["a", "b", "island"]
        edges = [("a", "b", 1)]
        distance, _ = bellman_ford(nodes, edges, "a")
        assert distance["island"] == math.inf


class TestPath:
    def test_reconstruct_the_route(self):
        nodes = ["a", "b", "c", "d"]
        edges = [("a", "b", 1), ("b", "c", 2), ("c", "d", 1)]
        _, predecessor = bellman_ford(nodes, edges, "a")
        assert reconstruct_path(predecessor, "a", "d") == ["a", "b", "c", "d"]

    def test_the_source_reaches_itself(self):
        nodes = ["a", "b"]
        edges = [("a", "b", 1)]
        _, predecessor = bellman_ford(nodes, edges, "a")
        assert reconstruct_path(predecessor, "a", "a") == ["a"]

    def test_an_unreachable_target_has_no_path(self):
        nodes = ["a", "b", "island"]
        edges = [("a", "b", 1)]
        _, predecessor = bellman_ford(nodes, edges, "a")
        assert reconstruct_path(predecessor, "a", "island") is None


class TestNegativeCycle:
    def test_a_negative_cycle_is_detected(self):
        nodes = ["a", "b", "c"]
        edges = [("a", "b", 1), ("b", "c", -3), ("c", "a", 1)]
        assert has_negative_cycle(nodes, edges, "a")
        with pytest.raises(Invalid):
            bellman_ford(nodes, edges, "a")

    def test_no_false_positive_on_a_negative_edge_without_a_cycle(self):
        nodes = ["a", "b", "c"]
        edges = [("a", "b", -2), ("b", "c", -3)]
        assert not has_negative_cycle(nodes, edges, "a")
