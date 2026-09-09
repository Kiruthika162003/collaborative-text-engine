from __future__ import annotations

from loom.author import Author
from loom.linenumbers import gutter_width, numbered, numbered_weave


class TestNumbered:
    def test_lines_get_a_number_gutter(self):
        assert numbered("a\nb") == "1  a\n2  b"

    def test_the_gutter_is_right_aligned(self):
        text = "\n".join(str(i) for i in range(1, 11))
        rendered = numbered(text)
        assert rendered.splitlines()[0].startswith(" 1  ")
        assert rendered.splitlines()[9].startswith("10  ")

    def test_a_custom_start_is_used(self):
        assert numbered("x\ny", start=5) == "5  x\n6  y"

    def test_blank_lines_are_numbered(self):
        assert numbered("a\n\nb") == "1  a\n2  \n3  b"


class TestWeave:
    def test_a_weave_is_numbered(self):
        author = Author(site="alice")
        author.type_at(0, "first\nsecond")
        assert numbered_weave(author.weave) == "1  first\n2  second"


class TestWidth:
    def test_gutter_width_grows_with_line_count(self):
        assert gutter_width("a") == 1
        assert gutter_width("\n".join("x" * 1 for _ in range(10))) == 2
