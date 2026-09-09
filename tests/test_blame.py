from __future__ import annotations

from loom.author import Author
from loom.blame import blame, blame_of_line, lines_by, render
from loom.circle import Circle


class TestSolo:
    def test_each_line_is_blamed_on_its_author(self):
        author = Author(site="alice")
        author.type_at(0, "hello\nworld")
        rows = blame(author.weave)
        assert [r.site for r in rows] == ["alice", "alice"]

    def test_an_empty_line_is_blamed_on_nobody(self):
        author = Author(site="alice")
        author.type_at(0, "a\n\nb")
        assert blame(author.weave)[1].site == ""


class TestShared:
    def duo(self) -> Circle:
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice", circle.author("alice").type_at(0, "abc")
        )
        circle.settle()
        return circle

    def test_the_majority_hand_takes_the_line(self):
        circle = self.duo()
        bob = circle.author("bob")
        circle.say("bob", bob.type_at(3, "de"))
        circle.settle()
        row = blame_of_line(circle.author("bob").weave, 0)
        assert row.site == "alice"
        assert row.share == 3
        assert row.total == 5

    def test_a_tie_breaks_to_the_first_site(self):
        circle = Circle.of(["alice", "bob"])
        circle.say("alice", circle.author("alice").type_at(0, "ab"))
        circle.settle()
        circle.say(
            "bob",
            circle.author("bob").type_at(
                circle.author("bob").weave.visible_count(), "cd"
            ),
        )
        circle.settle()
        assert blame_of_line(circle.author("alice").weave, 0).site == "alice"


class TestQueries:
    def test_lines_by_lists_an_authors_lines(self):
        author = Author(site="alice")
        author.type_at(0, "one\ntwo")
        assert lines_by(author.weave, "alice") == [0, 1]

    def test_render_shows_share_and_total(self):
        author = Author(site="alice")
        author.type_at(0, "hi")
        assert "0: alice (2/2)" in render(author.weave)

    def test_render_marks_blank_lines(self):
        author = Author(site="alice")
        author.type_at(0, "x\n\ny")
        assert "(blank)" in render(author.weave)
