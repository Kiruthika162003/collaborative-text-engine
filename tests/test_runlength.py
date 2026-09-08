from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.runlength import compression_ratio, fold, report


class TestFolding:
    def test_one_hands_run_folds_to_one_block(self):
        author = Author(site="alice")
        author.type_at(0, "aaaaaaaaaa")
        runs = fold(author.weave)
        assert len(runs) == 1
        assert runs[0].length() == 10
        assert runs[0].site == "alice"

    def test_a_site_change_breaks_the_run(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "abc"),
        )
        circle.settle()
        circle.say(
            "bob",
            circle.author("bob").type_at(3, "xyz"),
        )
        circle.settle()
        runs = fold(circle.author("alice").weave)
        sites = [run.site for run in runs]
        assert "alice" in sites
        assert "bob" in sites

    def test_a_shear_breaks_the_run(self):
        author = Author(site="alice")
        author.type_at(0, "abcde")
        author.erase_at(2, 1)
        runs = fold(author.weave)
        assert any(run.sheared for run in runs)
        assert any(not run.sheared for run in runs)

    def test_a_gap_in_counters_breaks_the_run(self):
        author = Author(site="alice")
        author.type_at(0, "ab")
        author.erase_at(0, 1)
        author.type_at(0, "z")
        runs = fold(author.weave)
        assert len(runs) >= 2


class TestRatios:
    def test_a_paragraph_compresses_well(self):
        author = Author(site="alice")
        author.type_at(0, "x" * 50)
        assert compression_ratio(author.weave) == 50.0

    def test_all_singletons_report_one(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "a"),
        )
        circle.say(
            "bob",
            circle.author("bob").type_at(0, "b"),
        )
        circle.settle()
        assert (
            compression_ratio(
                circle.author("alice").weave
            )
            == 1.0
        )

    def test_the_report_names_the_break_rule(self):
        author = Author(site="alice")
        author.type_at(0, "hello")
        page = report(author.weave)
        assert "5 strand(s) fold to 1 run(s)" in page
        assert "where convergence cares" in page

    def test_an_empty_fabric_folds_to_nothing(self):
        author = Author(site="alice")
        assert "folds to nothing" in report(
            author.weave
        )
