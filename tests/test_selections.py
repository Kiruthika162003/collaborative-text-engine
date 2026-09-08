from __future__ import annotations

from loom.author import Author
from loom.selections import Gallery


def galleried() -> tuple[Author, Gallery, list]:
    author = Author(site="alice")
    ops = author.type_at(0, "the shared sentence")
    return author, Gallery(weave=author.weave), ops


class TestSelecting:
    def test_a_selection_reads_its_text(self):
        _author, gallery, ops = galleried()
        gallery.select("bob", ops[4].id, ops[9].id)
        assert gallery.text_of("bob") == "shared"

    def test_a_selection_survives_upstream_edits(self):
        author, gallery, ops = galleried()
        gallery.select("bob", ops[4].id, ops[9].id)
        author.type_at(0, ">>> ")
        assert gallery.text_of("bob") == "shared"

    def test_a_collapsed_selection_is_a_cursor(self):
        _author, gallery, ops = galleried()
        gallery.select("bob", ops[0].id, ops[0].id)
        assert gallery.is_cursor("bob")
        assert "cursor, not selecting" in (
            gallery.sidebar()
        )

    def test_a_selection_on_the_dead_is_dropped(self):
        author, gallery, ops = galleried()
        gallery.select("bob", ops[4].id, ops[9].id)
        author.erase_at(4, 6)
        assert gallery.text_of("bob") == ""
        assert "nobody is selecting" in (
            gallery.sidebar()
        )

    def test_looking_away_clears_the_selection(self):
        _author, gallery, ops = galleried()
        gallery.select("bob", ops[0].id, ops[2].id)
        assert "looked away" in gallery.clear("bob")
        assert "bob" not in gallery.selections


class TestCollisions:
    def test_overlapping_selections_are_flagged(self):
        _author, gallery, ops = galleried()
        gallery.select("bob", ops[0].id, ops[9].id)
        gallery.select("cara", ops[4].id, ops[14].id)
        assert gallery.overlaps("bob", "cara")
        assert gallery.collisions() == [("bob", "cara")]
        assert (
            "a conflict is about to be typed"
            in gallery.sidebar()
        )

    def test_disjoint_selections_do_not_collide(self):
        _author, gallery, ops = galleried()
        gallery.select("bob", ops[0].id, ops[2].id)
        gallery.select("cara", ops[11].id, ops[14].id)
        assert not gallery.overlaps("bob", "cara")
        assert gallery.collisions() == []

    def test_the_sidebar_lists_present_hands(self):
        _author, gallery, ops = galleried()
        gallery.select("bob", ops[4].id, ops[9].id)
        gallery.select("cara", ops[11].id, ops[18].id)
        page = gallery.sidebar()
        assert "2 hand(s) present:" in page
        assert "bob: 'shared'" in page
        assert "cara: 'sentence'" in page
