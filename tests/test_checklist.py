from __future__ import annotations

import pytest

from loom.author import Author
from loom.checklist import Checklist, Toggle
from loom.errors import Missing
from loom.ids import OpId


def three_tasks() -> tuple[Author, Checklist, list]:
    author = Author(site="alice")
    ops = author.type_at(0, "- a\n- b\n- c")
    anchors = [ops[2].id, ops[6].id, ops[10].id]
    return author, Checklist(weave=author.weave), anchors


class TestToggling:
    def test_checking_marks_done(self):
        _author, chk, anchors = three_tasks()
        chk.toggle(
            Toggle(
                anchor=anchors[0],
                done=True,
                rank=1,
                site="alice",
            )
        )
        assert chk.is_done(anchors[0])
        assert not chk.is_done(anchors[1])

    def test_the_later_witness_wins_a_race(self):
        _author, chk, anchors = three_tasks()
        chk.toggle(
            Toggle(
                anchor=anchors[0],
                done=True,
                rank=2,
                site="alice",
            )
        )
        chk.toggle(
            Toggle(
                anchor=anchors[0],
                done=False,
                rank=5,
                site="bob",
            )
        )
        assert not chk.is_done(anchors[0])

    def test_an_early_toggle_yields(self):
        _author, chk, anchors = three_tasks()
        chk.toggle(
            Toggle(
                anchor=anchors[0],
                done=True,
                rank=9,
                site="alice",
            )
        )
        receipt = chk.toggle(
            Toggle(
                anchor=anchors[0],
                done=False,
                rank=2,
                site="bob",
            )
        )
        assert "yielded" in receipt
        assert chk.is_done(anchors[0])

    def test_a_free_checkmark_is_refused(self):
        _author, chk, _anchors = three_tasks()
        with pytest.raises(Missing):
            chk.toggle(
                Toggle(
                    anchor=OpId(site="zed", counter=9),
                    done=True,
                    rank=1,
                    site="zed",
                )
            )


class TestProgress:
    def test_progress_counts_the_living(self):
        _author, chk, anchors = three_tasks()
        chk.toggle(
            Toggle(
                anchor=anchors[0],
                done=True,
                rank=1,
                site="alice",
            )
        )
        assert chk.progress(anchors) == "1 of 3 done (33%)"

    def test_a_deleted_task_stops_counting(self):
        author, chk, anchors = three_tasks()
        chk.toggle(
            Toggle(
                anchor=anchors[0],
                done=True,
                rank=1,
                site="alice",
            )
        )
        author.erase_at(6, 1)
        assert chk.progress(anchors) == "1 of 2 done (50%)"

    def test_an_empty_list_has_nothing_to_do(self):
        author = Author(site="alice")
        author.type_at(0, "x")
        chk = Checklist(weave=author.weave)
        assert "nothing to do" in chk.progress([])
