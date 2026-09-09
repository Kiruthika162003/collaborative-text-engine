from __future__ import annotations

from loom.unionfind import UnionFind


def merged() -> UnionFind:
    uf = UnionFind()
    uf.union(1, 2)
    uf.union(2, 3)
    uf.union(4, 5)
    return uf


class TestConnectivity:
    def test_merged_items_are_connected(self):
        assert merged().connected(1, 3)

    def test_separate_groups_are_not_connected(self):
        assert not merged().connected(1, 4)

    def test_an_item_is_connected_to_itself(self):
        uf = UnionFind()
        assert uf.connected(9, 9)


class TestGroups:
    def test_group_count(self):
        assert merged().group_count() == 2

    def test_groups_list_their_members(self):
        groups = merged().groups()
        members = sorted(sorted(g) for g in groups.values())
        assert members == [[1, 2, 3], [4, 5]]

    def test_merging_two_groups_reduces_the_count(self):
        uf = merged()
        uf.union(3, 4)
        assert uf.group_count() == 1


class TestItems:
    def test_string_items_work(self):
        uf = UnionFind()
        uf.union("a", "b")
        assert uf.connected("a", "b")
