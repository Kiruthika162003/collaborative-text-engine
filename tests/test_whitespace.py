from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.whitespace import squeeze_spaces, trim_trailing


class TestTrim:
    def test_trailing_spaces_are_removed_per_line(self):
        author = Author(site="alice")
        author.type_at(0, "a  \nb \t\nc")
        trim_trailing(author)
        assert author.text() == "a\nb\nc"

    def test_trailing_whitespace_at_the_end_is_removed(self):
        author = Author(site="alice")
        author.type_at(0, "done   ")
        trim_trailing(author)
        assert author.text() == "done"

    def test_interior_spaces_are_left_by_trim(self):
        author = Author(site="alice")
        author.type_at(0, "a  b")
        trim_trailing(author)
        assert author.text() == "a  b"


class TestSqueeze:
    def test_internal_runs_collapse_to_one_space(self):
        author = Author(site="alice")
        author.type_at(0, "a  b   c")
        squeeze_spaces(author)
        assert author.text() == "a b c"

    def test_leading_indentation_is_spared(self):
        author = Author(site="alice")
        author.type_at(0, "    a  b")
        squeeze_spaces(author)
        assert author.text() == "    a b"

    def test_a_single_space_is_left_alone(self):
        author = Author(site="alice")
        author.type_at(0, "a b c")
        result = squeeze_spaces(author)
        assert result == []
        assert author.text() == "a b c"


class TestIdentity:
    def test_trim_leaves_visible_glyphs_and_their_ids(self):
        author = Author(site="alice")
        ops = author.type_at(0, "word   ")
        keep = ops[0].id
        trim_trailing(author)
        position = author.weave.by_id[keep]
        assert not author.weave.strands[position].sheared
        assert author.weave.strands[position].glyph == "w"


class TestConvergence:
    def test_a_trim_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "keep me   \nand me  "),
        )
        circle.settle()
        circle.say("alice", trim_trailing(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "keep me\nand me"
