from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.renumber import needs_renumber, renumber


class TestRenumber:
    def test_a_wrong_sequence_is_corrected(self):
        author = Author(site="alice")
        author.type_at(0, "1. a\n3. b\n2. c")
        renumber(author)
        assert author.text() == "1. a\n2. b\n3. c"

    def test_a_two_digit_number_is_replaced(self):
        author = Author(site="alice")
        author.type_at(0, "1. a\n9. b")
        renumber(author)
        assert author.text() == "1. a\n2. b"

    def test_nested_lists_count_apart(self):
        author = Author(site="alice")
        author.type_at(0, "1. a\n  1. x\n  5. y\n2. b")
        renumber(author)
        assert author.text() == "1. a\n  1. x\n  2. y\n2. b"

    def test_a_paragraph_break_restarts_the_count(self):
        author = Author(site="alice")
        author.type_at(0, "1. a\nprose\n1. b")
        assert not needs_renumber(author)


class TestNoop:
    def test_a_correct_list_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "1. a\n2. b\n3. c")
        assert renumber(author) == []

    def test_bullets_are_never_touched(self):
        author = Author(site="alice")
        author.type_at(0, "- a\n- b")
        assert renumber(author) == []


class TestNeeds:
    def test_needs_renumber_detects_a_wrong_number(self):
        author = Author(site="alice")
        author.type_at(0, "1. a\n1. b")
        assert needs_renumber(author)


class TestConvergence:
    def test_renumber_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "1. one\n1. two\n1. three"),
        )
        circle.settle()
        circle.say("alice", renumber(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "1. one\n2. two\n3. three"
