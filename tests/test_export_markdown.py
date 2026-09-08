from __future__ import annotations

from loom.author import Author
from loom.export_markdown import to_markdown, unknown_styles
from loom.ids import OpId
from loom.marks import Mark, Wardrobe


def dressed(style: str) -> Wardrobe:
    author = Author(site="alice")
    ops = author.type_at(0, "plain bold plain")
    wardrobe = Wardrobe(weave=author.weave)
    wardrobe.dress(
        Mark(
            id=OpId(site="alice", counter=100),
            style=style,
            start=ops[6].id,
            end=ops[9].id,
        )
    )
    return wardrobe


class TestKnownStyles:
    def test_bold_wraps_in_double_stars(self):
        assert to_markdown(dressed("bold")) == (
            "plain **bold** plain"
        )

    def test_italic_wraps_in_single_stars(self):
        assert to_markdown(dressed("italic")) == (
            "plain *bold* plain"
        )

    def test_plain_cloth_exports_unchanged(self):
        author = Author(site="alice")
        author.type_at(0, "nothing dressed here")
        wardrobe = Wardrobe(weave=author.weave)
        assert to_markdown(wardrobe) == (
            "nothing dressed here"
        )


class TestUnknownStyles:
    def test_unknown_styles_are_dropped_loudly(self):
        wardrobe = dressed("highlight")
        page = to_markdown(wardrobe)
        assert page.startswith("plain bold plain")
        assert "unexported styles dropped: highlight" in (
            page
        )
        assert "becomes a paragraph" in page

    def test_the_unknown_list_is_reported(self):
        assert unknown_styles(dressed("highlight")) == [
            "highlight"
        ]
        assert unknown_styles(dressed("bold")) == []

    def test_a_known_and_unknown_mix_keeps_the_known(
        self,
    ):
        author = Author(site="alice")
        ops = author.type_at(0, "plain bold plain")
        wardrobe = Wardrobe(weave=author.weave)
        wardrobe.dress(
            Mark(
                id=OpId(site="alice", counter=100),
                style="bold",
                start=ops[6].id,
                end=ops[9].id,
            )
        )
        wardrobe.dress(
            Mark(
                id=OpId(site="bob", counter=50),
                style="secret",
                start=ops[6].id,
                end=ops[9].id,
            )
        )
        page = to_markdown(wardrobe)
        assert "**bold**" in page
        assert "secret" in page
