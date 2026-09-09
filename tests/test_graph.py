from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.graph import Graph


class TestTopoSort:
    def test_a_dag_orders_dependencies_first(self):
        graph = Graph()
        graph.add_edge("a", "b")
        graph.add_edge("b", "c")
        graph.add_edge("a", "c")
        assert graph.topological_sort() == ["a", "b", "c"]

    def test_the_order_is_deterministic(self):
        graph = Graph()
        graph.add_edge("a", "c")
        graph.add_edge("b", "c")
        assert graph.topological_sort() == ["a", "b", "c"]

    def test_an_isolated_node_appears(self):
        graph = Graph()
        graph.add_edge("a", "b")
        graph.add_node("z")
        assert "z" in graph.topological_sort()


class TestCycles:
    def test_a_cycle_has_no_order(self):
        graph = Graph()
        graph.add_edge("a", "b")
        graph.add_edge("b", "a")
        with pytest.raises(Invalid):
            graph.topological_sort()

    def test_has_cycle_detects_it(self):
        graph = Graph()
        graph.add_edge("a", "b")
        graph.add_edge("b", "a")
        assert graph.has_cycle()

    def test_a_dag_has_no_cycle(self):
        graph = Graph()
        graph.add_edge("a", "b")
        assert not graph.has_cycle()


class TestAccess:
    def test_neighbors_and_nodes(self):
        graph = Graph()
        graph.add_edge("a", "b")
        graph.add_edge("a", "c")
        assert graph.neighbors("a") == ["b", "c"]
        assert graph.nodes() == ["a", "b", "c"]
