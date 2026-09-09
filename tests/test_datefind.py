from __future__ import annotations

from loom.author import Author
from loom.datefind import ambiguous, dates, normalized, report


class TestFormats:
    def test_iso_dates_are_found(self):
        author = Author(site="alice")
        author.type_at(0, "on 2024-03-12 we met")
        assert dates(author.weave)[0].iso == "2024-03-12"

    def test_day_month_year_normalizes(self):
        author = Author(site="alice")
        author.type_at(0, "due 12 March 2024")
        assert dates(author.weave)[0].iso == "2024-03-12"

    def test_month_day_year_normalizes(self):
        author = Author(site="alice")
        author.type_at(0, "due March 12, 2024")
        assert dates(author.weave)[0].iso == "2024-03-12"

    def test_an_abbreviated_month_is_understood(self):
        author = Author(site="alice")
        author.type_at(0, "due 12 Mar 2024")
        assert dates(author.weave)[0].iso == "2024-03-12"


class TestSlash:
    def test_a_settled_slash_date_normalizes(self):
        author = Author(site="alice")
        author.type_at(0, "ship 25/12/2024")
        found = dates(author.weave)[0]
        assert found.iso == "2024-12-25"
        assert not found.ambiguous

    def test_an_ambiguous_slash_date_is_flagged_not_guessed(self):
        author = Author(site="alice")
        author.type_at(0, "meet 05/06/2024")
        found = dates(author.weave)[0]
        assert found.iso is None
        assert found.ambiguous


class TestRollups:
    def test_normalized_drops_the_ambiguous(self):
        author = Author(site="alice")
        author.type_at(0, "a 2024-01-01 and b 05/06/2024")
        assert normalized(author.weave) == ["2024-01-01"]

    def test_ambiguous_lists_the_uncertain(self):
        author = Author(site="alice")
        author.type_at(0, "05/06/2024 and 25/12/2024")
        assert len(ambiguous(author.weave)) == 1


class TestPinAndReport:
    def test_a_date_pins_and_survives_upstream_edits(self):
        author = Author(site="alice")
        author.type_at(0, "on 2024-03-12")
        pin = dates(author.weave)[0].pin
        author.type_at(0, "PRE ")
        assert dates(author.weave)[0].pin == pin

    def test_the_report_counts_dates_and_ambiguity(self):
        author = Author(site="alice")
        author.type_at(0, "2024-01-01 and 05/06/2024")
        page = report(author.weave)
        assert "2 date(s), 1 ambiguous" in page

    def test_a_dateless_document_says_so(self):
        author = Author(site="alice")
        author.type_at(0, "no dates here")
        assert "no dates found" in report(author.weave)
