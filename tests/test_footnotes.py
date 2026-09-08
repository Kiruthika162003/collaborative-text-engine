from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Invalid, Missing
from loom.footnotes import Apparatus, Note
from loom.ids import OpId


def annotated() -> tuple[Author, Apparatus, list]:
    author = Author(site="alice")
    ops = author.type_at(0, "alpha beta gamma")
    app = Apparatus(weave=author.weave)
    app.add(
        Note(
            id=OpId(site="bob", counter=1),
            anchor=ops[4].id,
            body="on alpha",
        )
    )
    app.add(
        Note(
            id=OpId(site="bob", counter=2),
            anchor=ops[14].id,
            body="on gamma",
        )
    )
    return author, app, ops


class TestNumbering:
    def test_notes_number_by_reading_order(self):
        _author, app, _ops = annotated()
        page = app.apparatus()
        assert "[1] on alpha" in page
        assert "[2] on gamma" in page

    def test_a_note_inserted_earlier_renumbers(self):
        _author, app, ops = annotated()
        app.add(
            Note(
                id=OpId(site="cara", counter=1),
                anchor=ops[0].id,
                body="on the very start",
            )
        )
        page = app.apparatus()
        assert "[1] on the very start" in page
        assert "[2] on alpha" in page
        assert "[3] on gamma" in page

    def test_an_empty_note_is_refused(self):
        _author, _app, ops = annotated()
        with pytest.raises(Invalid):
            Note(
                id=OpId(site="bob", counter=9),
                anchor=ops[0].id,
                body="   ",
            )

    def test_an_unanchored_note_buffers(self):
        _author, app, _ops = annotated()
        with pytest.raises(Missing):
            app.add(
                Note(
                    id=OpId(site="bob", counter=9),
                    anchor=OpId(site="zed", counter=9),
                    body="ghost",
                )
            )


class TestOrphans:
    def test_a_deleted_anchor_orphans_its_note(self):
        author, app, _ops = annotated()
        author.erase_at(0, 5)
        assert len(app.orphaned()) == 1
        page = app.apparatus()
        assert "[orphaned] on alpha" in page
        assert "[1] on gamma" in page

    def test_the_census_counts_both_kinds(self):
        author, app, _ops = annotated()
        author.erase_at(0, 5)
        assert app.census() == (
            "1 live footnote(s), 1 orphaned by "
            "deletion"
        )
