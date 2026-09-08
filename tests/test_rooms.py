from __future__ import annotations

from loom.cli import main
from loom.rooms import (
    day_names,
    days,
    directory,
    itinerary,
    workshop,
)


class TestTheDirectory:
    def test_known_rooms_speak_their_own_lines(self):
        table = dict(workshop())
        assert table["weave"].startswith("The weave:")
        assert table["gravedigger"].startswith(
            "The gravedigger:"
        )
        assert "mailroom" in table

    def test_no_room_is_nameless(self):
        for name, headline in workshop():
            assert not headline.startswith(
                "UNDOCUMENTED"
            ), name

    def test_the_mirror_rooms_stay_off_the_roster(self):
        names = [name for name, _headline in workshop()]
        assert "cli" not in names
        assert "rooms" not in names
        assert "trials" not in names

    def test_the_headline_counts_honestly(self):
        page = directory()
        first = page.splitlines()[0]
        assert first.endswith("0 undocumented:")
        assert int(first.split(" ")[0]) >= 30


class TestTheItinerary:
    def test_every_day_says_how_to_run_it(self):
        page = itinerary()
        assert (
            "every day says how to run it; nothing "
            "here is furniture"
        ) in page

    def test_the_days_are_on_record(self):
        assert "pairday" in day_names()
        assert "trainday" in day_names()
        assert len(days()) >= 2


class TestTheCli:
    def test_the_rooms_verb_opens_the_directory(
        self, capsys
    ):
        assert main(["rooms"]) == 0
        out = capsys.readouterr().out
        assert "room(s), 0 undocumented:" in out
        assert "postmaster:" in out

    def test_the_days_verb_opens_the_itinerary(
        self, capsys
    ):
        assert main(["days"]) == 0
        out = capsys.readouterr().out
        assert "day(s) on record:" in out
        assert "trainday:" in out
