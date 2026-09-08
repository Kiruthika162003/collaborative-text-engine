from __future__ import annotations

from loom.metamap import MetaMap


class TestPerKeyWinners:
    def test_the_higher_rank_wins_a_key(self):
        m = MetaMap()
        m.set("color", "red", rank=2, site="alice")
        m.set("color", "blue", rank=5, site="bob")
        assert m.get("color") == "blue"

    def test_keys_settle_independently(self):
        m = MetaMap()
        m.set("color", "red", rank=9, site="alice")
        m.set("folder", "inbox", rank=1, site="bob")
        assert m.get("color") == "red"
        assert m.get("folder") == "inbox"

    def test_rank_ties_break_by_site(self):
        one = MetaMap()
        one.set("k", "A", rank=4, site="alice")
        one.set("k", "B", rank=4, site="bob")
        assert one.get("k") == "B"


class TestDeletion:
    def test_a_tombstone_hides_the_key(self):
        m = MetaMap()
        m.set("due", "friday", rank=1, site="alice")
        m.delete("due", rank=2, site="alice")
        assert not m.has("due")
        assert m.get("due", "none") == "none"

    def test_a_later_set_beats_a_delete(self):
        m = MetaMap()
        m.set("due", "friday", rank=1, site="alice")
        m.delete("due", rank=2, site="alice")
        m.set("due", "monday", rank=3, site="bob")
        assert m.get("due") == "monday"


class TestMerge:
    def test_merge_takes_the_winner_per_key(self):
        one = MetaMap()
        one.set("a", "x", rank=5, site="alice")
        one.set("b", "y", rank=1, site="alice")
        two = MetaMap()
        two.set("a", "z", rank=2, site="bob")
        two.set("b", "w", rank=9, site="bob")
        one.merge(two)
        assert one.get("a") == "x"
        assert one.get("b") == "w"

    def test_merge_is_commutative_and_idempotent(self):
        a = MetaMap()
        a.set("k", "A", rank=3, site="alice")
        b = MetaMap()
        b.set("k", "B", rank=7, site="bob")
        left = a.copy()
        left.merge(b)
        left.merge(b)
        right = b.copy()
        right.merge(a)
        assert left.get("k") == right.get("k") == "B"

    def test_keys_lists_only_the_living(self):
        m = MetaMap()
        m.set("a", 1, rank=1, site="alice")
        m.set("b", 2, rank=1, site="alice")
        m.delete("a", rank=2, site="alice")
        assert m.keys() == ["b"]
