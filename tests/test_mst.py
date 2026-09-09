from __future__ import annotations

from loom.mst import is_spanning, minimum_spanning_tree


class TestMinimumSpanningTree:
    def test_a_small_weighted_graph(self):
        nodes = ["a", "b", "c", "d"]
        edges = [
            (1, "a", "b"),
            (3, "a", "c"),
            (4, "b", "c"),
            (2, "c", "d"),
            (5, "b", "d"),
        ]
        chosen, total = minimum_spanning_tree(nodes, edges)
        assert total == 1 + 3 + 2
        assert is_spanning(nodes, chosen)

    def test_the_tree_has_one_fewer_edge_than_nodes(self):
        nodes = [1, 2, 3, 4, 5]
        edges = [
            (2, 1, 2),
            (3, 2, 3),
            (1, 3, 4),
            (4, 4, 5),
            (6, 1, 5),
            (5, 2, 4),
        ]
        chosen, _ = minimum_spanning_tree(nodes, edges)
        assert len(chosen) == 4
        assert is_spanning(nodes, chosen)

    def test_the_cheapest_edges_win_ties_by_order(self):
        nodes = ["x", "y", "z"]
        edges = [(1, "x", "y"), (1, "y", "z"), (1, "x", "z")]
        chosen, total = minimum_spanning_tree(nodes, edges)
        assert total == 2
        assert len(chosen) == 2


class TestForest:
    def test_a_disconnected_graph_yields_a_forest(self):
        nodes = ["a", "b", "c", "d"]
        # two separate pairs, no edge between them
        edges = [(1, "a", "b"), (2, "c", "d")]
        chosen, total = minimum_spanning_tree(nodes, edges)
        assert total == 3
        assert len(chosen) == 2
        assert not is_spanning(nodes, chosen)

    def test_a_cycle_edge_is_skipped(self):
        nodes = ["a", "b", "c"]
        edges = [(1, "a", "b"), (2, "b", "c"), (3, "a", "c")]
        chosen, total = minimum_spanning_tree(nodes, edges)
        assert total == 3
        assert (3, "a", "c") not in chosen
