from __future__ import annotations

from loom.scc import is_strongly_connected, strongly_connected_components


class TestComponents:
    def test_a_single_cycle_is_one_component(self):
        graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
        assert strongly_connected_components(graph) == [["a", "b", "c"]]
        assert is_strongly_connected(graph)

    def test_a_chain_is_all_singletons(self):
        graph = {"a": ["b"], "b": ["c"], "c": []}
        assert strongly_connected_components(graph) == [["a"], ["b"], ["c"]]
        assert not is_strongly_connected(graph)

    def test_two_cycles_joined_by_a_one_way_bridge(self):
        graph = {
            "a": ["b"],
            "b": ["a", "c"],
            "c": ["d"],
            "d": ["c"],
        }
        assert strongly_connected_components(graph) == [["a", "b"], ["c", "d"]]

    def test_a_classic_multi_component_graph(self):
        graph = {
            1: [2],
            2: [3, 4],
            3: [1],
            4: [5],
            5: [6],
            6: [4, 7],
            7: [],
        }
        components = strongly_connected_components(graph)
        assert [1, 2, 3] in components
        assert [4, 5, 6] in components
        assert [7] in components
        assert len(components) == 3


class TestEdges:
    def test_nodes_that_appear_only_as_targets(self):
        graph = {"a": ["b"]}
        assert strongly_connected_components(graph) == [["a"], ["b"]]

    def test_a_self_loop_is_its_own_component(self):
        graph = {"a": ["a"], "b": []}
        assert strongly_connected_components(graph) == [["a"], ["b"]]

    def test_the_empty_graph(self):
        assert strongly_connected_components({}) == []


class TestDeterminism:
    def test_insertion_order_does_not_change_the_grouping(self):
        forward = {"a": ["b"], "b": ["a"], "c": ["a"]}
        backward = {"c": ["a"], "b": ["a"], "a": ["b"]}
        assert strongly_connected_components(forward) == strongly_connected_components(backward)
