from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Invalid, Missing
from loom.ids import OpId
from loom.marks import Mark, Unmark, Wardrobe


def dressed_author() -> tuple[Author, Wardrobe, list]:
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
    return author, wardrobe, ops


class TestDressing:
    def test_spans_read_like_a_renderer_would(self):
        _author, wardrobe, _ops = dressed_author()
        assert wardrobe.spans() == [
            ("plain ", frozenset()),
            ("bold", frozenset({"bold"})),
            (" plain", frozenset()),
        ]

    def test_typing_inside_the_dress_wears_it(self):
        author, wardrobe, _ops = dressed_author()
        author.type_at(8, "!!")
        spans = dict(wardrobe.spans())
        assert spans["bo!!ld"] == frozenset({"bold"})

    def test_a_backwards_pin_is_refused(self):
        author = Author(site="alice")
        ops = author.type_at(0, "abc")
        wardrobe = Wardrobe(weave=author.weave)
        with pytest.raises(Invalid) as caught:
            wardrobe.dress(
                Mark(
                    id=OpId(site="alice", counter=99),
                    style="bold",
                    start=ops[2].id,
                    end=ops[0].id,
                )
            )
        assert "will turn it around" in str(caught.value)

    def test_an_unpinned_strand_is_a_buffer_cue(self):
        author = Author(site="alice")
        author.type_at(0, "a")
        wardrobe = Wardrobe(weave=author.weave)
        with pytest.raises(Missing):
            wardrobe.dress(
                Mark(
                    id=OpId(site="bob", counter=1),
                    style="bold",
                    start=OpId(site="bob", counter=9),
                    end=OpId(site="bob", counter=9),
                )
            )

    def test_styles_are_shared_vocabulary(self):
        with pytest.raises(Invalid):
            Mark(
                id=OpId(site="alice", counter=1),
                style="BOLD",
                start=OpId(site="alice", counter=1),
                end=OpId(site="alice", counter=1),
            )

    def test_dressing_twice_dresses_once(self):
        _author, wardrobe, ops = dressed_author()
        receipt = wardrobe.dress(
            Mark(
                id=OpId(site="alice", counter=100),
                style="bold",
                start=ops[6].id,
                end=ops[9].id,
            )
        )
        assert "one mark, one instance" in receipt


class TestStripping:
    def test_strip_removes_by_instance(self):
        _author, wardrobe, _ops = dressed_author()
        wardrobe.strip(
            Unmark(
                id=OpId(site="bob", counter=1),
                mark_id=OpId(site="alice", counter=100),
            )
        )
        assert wardrobe.spans() == [
            ("plain bold plain", frozenset())
        ]

    def test_a_concurrent_dressing_survives_the_strip(
        self,
    ):
        _author, wardrobe, ops = dressed_author()
        wardrobe.dress(
            Mark(
                id=OpId(site="bob", counter=50),
                style="bold",
                start=ops[6].id,
                end=ops[9].id,
            )
        )
        wardrobe.strip(
            Unmark(
                id=OpId(site="bob", counter=51),
                mark_id=OpId(site="alice", counter=100),
            )
        )
        spans = dict(wardrobe.spans())
        assert spans["bold"] == frozenset({"bold"})

    def test_stripping_the_unseen_is_a_buffer_cue(self):
        _author, wardrobe, _ops = dressed_author()
        with pytest.raises(Missing):
            wardrobe.strip(
                Unmark(
                    id=OpId(site="bob", counter=1),
                    mark_id=OpId(site="zed", counter=9),
                )
            )


class TestDeadPins:
    def test_a_tombstoned_pin_keeps_serving(self):
        author, wardrobe, _ops = dressed_author()
        author.erase_at(6, 1)
        spans = dict(wardrobe.spans())
        assert spans["old"] == frozenset({"bold"})
        assert "1 mark(s) standing" in wardrobe.census()
