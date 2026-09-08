from __future__ import annotations

import pytest

from loom.author import Author
from loom.comments import Comment, Margin
from loom.errors import Invalid, Missing
from loom.ids import OpId


def commented() -> tuple[Author, Margin, list]:
    author = Author(site="alice")
    ops = author.type_at(0, "the weak word here")
    margin = Margin(weave=author.weave)
    root = Comment(
        id=OpId(site="bob", counter=90),
        author="bob",
        body="reconsider this",
        first=ops[4].id,
        last=ops[7].id,
    )
    margin.add(root)
    return author, margin, ops


class TestPinning:
    def test_a_comment_quotes_the_stretch(self):
        _author, margin, _ops = commented()
        page = margin.render()
        assert "bob on 'weak'" in page
        assert "reconsider this" in page

    def test_the_quote_survives_upstream_edits(self):
        author, margin, _ops = commented()
        author.type_at(0, ">>> ")
        page = margin.render()
        assert "bob on 'weak'" in page
        assert "STALE" not in page

    def test_an_edited_stretch_goes_stale_not_wrong(
        self,
    ):
        author, margin, _ops = commented()
        author.erase_at(4, 4)
        assert margin.is_stale(
            OpId(site="bob", counter=90)
        )
        assert "STALE" in margin.render()

    def test_an_empty_remark_is_refused(self):
        _author, _margin, ops = commented()
        with pytest.raises(Invalid):
            Comment(
                id=OpId(site="bob", counter=91),
                author="bob",
                body="  ",
                first=ops[0].id,
                last=ops[0].id,
            )

    def test_an_unpinned_comment_buffers(self):
        _author, margin, _ops = commented()
        with pytest.raises(Missing):
            margin.add(
                Comment(
                    id=OpId(site="bob", counter=92),
                    author="bob",
                    body="ghost",
                    first=OpId(site="zed", counter=9),
                    last=OpId(site="zed", counter=9),
                )
            )


class TestThreads:
    def test_replies_render_in_order(self):
        _author, margin, ops = commented()
        parent = OpId(site="bob", counter=90)
        margin.add(
            Comment(
                id=OpId(site="cara", counter=1),
                author="cara",
                body="agreed",
                first=ops[4].id,
                last=ops[7].id,
                parent=parent,
            )
        )
        page = margin.render()
        assert "    cara: agreed" in page

    def test_a_reply_needs_a_parent(self):
        _author, margin, ops = commented()
        with pytest.raises(Missing):
            margin.add(
                Comment(
                    id=OpId(site="cara", counter=2),
                    author="cara",
                    body="orphan",
                    first=ops[0].id,
                    last=ops[0].id,
                    parent=OpId(
                        site="nobody", counter=1
                    ),
                )
            )

    def test_resolving_settles_the_thread_not_the_cloth(
        self,
    ):
        author, margin, _ops = commented()
        receipt = margin.resolve(
            OpId(site="bob", counter=90), by="alice"
        )
        assert "the cloth does not" in receipt
        assert "[resolved" in margin.render()
        assert author.text() == "the weak word here"
