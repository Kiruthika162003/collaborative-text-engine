from __future__ import annotations

import pytest

from loom.author import Author
from loom.checkpoints import Shelf
from loom.errors import Invalid, Missing
from loom.versions import Timeline


def drafted() -> tuple[Author, Timeline]:
    author = Author(site="alice")
    timeline = Timeline(shelf=Shelf())
    author.type_at(0, "the first words")
    timeline.capture("draft-1", author.weave)
    author.type_at(
        author.weave.visible_count(), " and more"
    )
    timeline.capture("draft-2", author.weave)
    return author, timeline


class TestWalking:
    def test_the_cursor_walks_back_and_forth(self):
        _author, tl = drafted()
        assert tl.current() == "draft-2"
        assert "draft-1" in tl.back()
        assert "draft-2" in tl.forward()

    def test_the_ends_clamp_and_say_so(self):
        _author, tl = drafted()
        tl.back()
        assert "nothing earlier" in tl.back()
        tl.forward()
        assert "nothing later" in tl.forward()

    def test_goto_a_named_version(self):
        _author, tl = drafted()
        assert "draft-1" in tl.goto("draft-1")
        assert tl.current() == "draft-1"

    def test_an_unknown_version_is_refused(self):
        _author, tl = drafted()
        with pytest.raises(Missing):
            tl.goto("draft-9")


class TestDiffing:
    def test_the_step_diff_reads_word_level(self):
        _author, tl = drafted()
        page = tl.step_diff()
        assert "from 'draft-1' to 'draft-2'" in page
        assert "added" in page

    def test_the_first_draft_has_nothing_before(self):
        _author, tl = drafted()
        tl.goto("draft-1")
        assert "nothing before it" in tl.step_diff()


class TestTheTimeline:
    def test_the_timeline_marks_the_cursor(self):
        _author, tl = drafted()
        tl.back()
        page = tl.timeline()
        assert "0: draft-1 <- here" in page
        assert "1: draft-2" in page

    def test_an_empty_timeline_says_so(self):
        tl = Timeline(shelf=Shelf())
        assert "no versions captured" in tl.timeline()
        with pytest.raises(Invalid):
            tl.current()
