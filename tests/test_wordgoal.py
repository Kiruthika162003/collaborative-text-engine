from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Invalid
from loom.wordgoal import WordGoal


def goaled(target: int) -> tuple[Author, WordGoal]:
    author = Author(site="alice")
    return author, WordGoal(weave=author.weave, target=target)


class TestProgress:
    def test_progress_reads_the_living_cloth(self):
        author, goal = goaled(10)
        author.type_at(0, "one two three")
        assert goal.written() == 3
        assert goal.remaining() == 7

    def test_deleting_walks_progress_backward(self):
        author, goal = goaled(10)
        author.type_at(0, "one two three four")
        author.erase_at(0, 8)
        assert goal.written() == 2

    def test_a_zero_goal_is_refused(self):
        author = Author(site="alice")
        with pytest.raises(Invalid):
            WordGoal(weave=author.weave, target=0)


class TestMilestones:
    def test_milestones_fire_once_upward(self):
        author, goal = goaled(4)
        author.type_at(0, "one")
        assert goal.check_milestones() == [25]
        author.type_at(
            author.weave.visible_count(),
            " two three four",
        )
        assert goal.check_milestones() == [50, 75, 100]

    def test_a_fired_milestone_does_not_refire(self):
        author, goal = goaled(4)
        author.type_at(0, "one two")
        goal.check_milestones()
        assert goal.check_milestones() == []

    def test_deleting_below_rearms_quietly(self):
        author, goal = goaled(4)
        author.type_at(0, "one two three four")
        assert goal.check_milestones() == [
            25,
            50,
            75,
            100,
        ]
        author.erase_at(0, author.weave.visible_count())
        assert goal.written() == 0
        goal.check_milestones()
        author.type_at(0, "one two three four")
        assert goal.check_milestones() == [
            25,
            50,
            75,
            100,
        ]


class TestReport:
    def test_the_report_shows_the_fraction(self):
        author, goal = goaled(10)
        author.type_at(0, "three words here")
        assert "3 of 10 words (30%)" in goal.report()

    def test_overshooting_is_celebrated(self):
        author, goal = goaled(2)
        author.type_at(0, "one two three four")
        report = goal.report()
        assert "goal met with 2 to spare" in report
        assert "doing more" in report
