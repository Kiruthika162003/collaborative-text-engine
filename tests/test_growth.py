from __future__ import annotations

from loom.author import Author
from loom.growth import churn, growth_curve, net_growth, peak, report
from loom.transcript import Tape


def session() -> Tape:
    tape = Tape()
    author = Author(site="alice", tape=tape)
    author.type_at(0, "hello")
    author.erase_at(0, 2)
    return tape


class TestCurve:
    def test_the_curve_rises_and_falls(self):
        assert growth_curve(session()) == [1, 2, 3, 4, 5, 4, 3]

    def test_an_empty_tape_has_no_curve(self):
        assert growth_curve(Tape()) == []


class TestNumbers:
    def test_net_growth_is_where_the_curve_ends(self):
        assert net_growth(session()) == 3

    def test_churn_counts_the_deletions(self):
        assert churn(session()) == 2

    def test_peak_names_the_high_point_and_when(self):
        assert peak(session()) == (5, 4)

    def test_an_empty_tape_nets_zero(self):
        assert net_growth(Tape()) == 0
        assert peak(Tape()) == (0, -1)


class TestReport:
    def test_the_report_names_the_axis(self):
        page = report(session())
        assert "net growth 3" in page
        assert "operation order" in page

    def test_an_empty_tape_reports_no_growth(self):
        assert "no growth" in report(Tape())
