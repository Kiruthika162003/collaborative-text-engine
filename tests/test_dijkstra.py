from __future__ import annotations

from loom.dijkstra import shortest_distance, shortest_paths

GRAPH = {
    "a": [("b", 1), ("c", 4)],
    "b": [("c", 2), ("d", 5)],
    "c": [("d", 1)],
    "d": [],
}


class TestShortestPaths:
    def test_distances_from_the_source(self):
        assert shortest_paths(GRAPH, "a") == {"a": 0, "b": 1, "c": 3, "d": 4}

    def test_a_cheaper_indirect_path_wins(self):
        # a to c is 3 through b, not the direct 4
        assert shortest_paths(GRAPH, "a")["c"] == 3

    def test_an_unreachable_node_is_absent(self):
        graph = {"a": [("b", 1)], "b": [], "island": []}
        assert "island" not in shortest_paths(graph, "a")


class TestShortestDistance:
    def test_the_distance_between_two_nodes(self):
        assert shortest_distance(GRAPH, "a", "d") == 4

    def test_an_unreachable_end_is_none(self):
        graph = {"a": [], "b": []}
        assert shortest_distance(graph, "a", "b") is None

    def test_the_source_to_itself_is_zero(self):
        assert shortest_distance(GRAPH, "a", "a") == 0
