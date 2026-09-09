from __future__ import annotations

from loom.author import Author
from loom.hotspots import (
    contested_count,
    hotspots,
    report,
    sites_in_contention,
)


def collide() -> tuple[Author, Author]:
    alice = Author(site="alice")
    bob = Author(site="bob")
    alice_ops = alice.type_at(0, "XY")
    bob_ops = bob.type_at(0, "Z")
    for op in alice_ops:
        bob.absorb(op)
    for op in bob_ops:
        alice.absorb(op)
    return alice, bob


class TestHotspots:
    def test_a_solo_run_is_not_a_hotspot(self):
        author = Author(site="alice")
        author.type_at(0, "a long solo run of typing")
        assert hotspots(author.weave) == []

    def test_two_hands_at_one_point_make_a_hotspot(self):
        alice, _bob = collide()
        spots = hotspots(alice.weave)
        assert len(spots) == 1
        assert spots[0].sites == ("alice", "bob")

    def test_both_replicas_see_the_same_hotspot(self):
        alice, bob = collide()
        assert hotspots(alice.weave) == hotspots(bob.weave)


class TestQueries:
    def test_contested_count_totals_the_hotspots(self):
        alice, _bob = collide()
        assert contested_count(alice.weave) == 1

    def test_sites_in_contention_lists_the_hands(self):
        alice, _bob = collide()
        assert sites_in_contention(alice.weave) == {"alice", "bob"}

    def test_a_tombstoned_contest_still_counts(self):
        alice, _bob = collide()
        alice.erase_at(0, 1)
        assert contested_count(alice.weave) == 1


class TestReport:
    def test_the_report_names_the_hands(self):
        alice, _bob = collide()
        page = report(alice.weave)
        assert "alice, bob" in page
        assert "concurrency, not trouble" in page

    def test_a_solo_document_reports_no_hotspots(self):
        author = Author(site="alice")
        author.type_at(0, "alone here")
        assert "no two hands" in report(author.weave)
