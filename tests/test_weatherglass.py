from __future__ import annotations

from loom.circle import Circle
from loom.weatherglass import (
    forecast,
    in_flight,
    report,
    shelved,
)


def working_circle() -> Circle:
    circle = Circle.of(
        ["alice", "bob", "cara"],
        temperament="gremlin",
        seed=31,
    )
    circle.say(
        "alice",
        circle.author("alice").type_at(0, "front"),
    )
    return circle


class TestReadings:
    def test_flight_and_shelf_are_read_separately(self):
        circle = working_circle()
        assert in_flight(circle) == 10
        assert shelved(circle) == 0
        assert forecast(circle).startswith(
            "mail in flight: 10"
        )

    def test_settling_clears_the_glass(self):
        circle = working_circle()
        circle.settle()
        assert forecast(circle) == (
            "all quiet; nothing rides, nothing waits"
        )

    def test_a_backlog_names_both_numbers(self):
        circle = Circle.of(["alice", "bob"])
        ops = circle.author("alice").type_at(0, "abc")
        circle.mailrooms["bob"].receive(ops[2])
        assert shelved(circle) == 1
        assert forecast(circle).startswith(
            "shelf backlog: 1 arrival(s)"
        )


class TestTheReport:
    def test_the_instruments_are_read_not_invented(
        self,
    ):
        circle = working_circle()
        circle.settle()
        page = report(circle)
        assert (
            "6 link(s) under gremlin weather" in page
        )
        assert "10 posted, " in page
        assert "duplicate(s) manufactured" in page
        assert "busiest: alice -> " in page
        assert "forecast: all quiet" in page
        assert (
            "a mood without a measurement is nothing"
        ) in page
