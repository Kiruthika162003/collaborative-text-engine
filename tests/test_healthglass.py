from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.healthglass import health


def coauthored() -> Circle:
    circle = Circle.of(["alice", "bob"])
    circle.say(
        "alice",
        circle.author("alice").type_at(
            0, "first thought\n\nsecond thought"
        ),
    )
    circle.settle()
    circle.say(
        "bob",
        circle.author("bob").type_at(13, " indeed"),
    )
    circle.settle()
    return circle


class TestTheGlass:
    def test_every_examiner_speaks_in_its_own_words(
        self,
    ):
        weave = coauthored().author("alice").weave
        page = health(weave)
        assert "structure:" in page
        assert "voices:" in page
        assert "writing:" in page
        assert "shape:" in page
        assert "hand(s) ever touched the cloth" in page
        assert "run(s) of voice" in page
        assert "word(s) on" in page
        assert "paragraph(s):" in page

    def test_the_glass_counts_but_never_grades(self):
        weave = coauthored().author("alice").weave
        page = health(weave)
        assert "4 examiner(s) reported" in page
        assert "conversation ender" in page
        assert "no grade" in page
        closing = page.splitlines()[-1]
        assert "score" not in closing.lower()

    def test_the_empty_page_is_all_future(self):
        author = Author(site="alice")
        page = health(author.weave)
        assert "0-glyph fabric" in page
        assert "every future is open" in page
