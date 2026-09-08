from __future__ import annotations

import pytest

from loom.errors import Missing
from loom.library import Library, sync_libraries


def stocked() -> Library:
    library = Library(site="alice")
    library.open_doc("plan")
    library.type_in("plan", 0, "ship tuesday")
    library.open_doc("notes")
    library.type_in("notes", 0, "remember the fox")
    return library


class TestShelves:
    def test_documents_keep_to_their_own_weaves(self):
        library = stocked()
        assert library.docs["plan"].text() == (
            "ship tuesday"
        )
        assert library.docs["notes"].text() == (
            "remember the fox"
        )

    def test_opening_twice_is_arriving_twice(self):
        library = stocked()
        again = library.open_doc("plan")
        assert again is library.docs["plan"]

    def test_typos_never_become_residents(self):
        library = stocked()
        with pytest.raises(Missing) as caught:
            library.type_in("plna", 0, "oops")
        message = str(caught.value)
        assert "'plan'" in message
        assert "permanent residents" in message

    def test_burning_is_loud_and_final(self):
        library = stocked()
        receipt = library.burn("notes")
        assert "'notes' burned" in receipt
        with pytest.raises(Missing):
            library.type_in("notes", 0, "ghost")

    def test_the_catalogue_counts_words(self):
        library = stocked()
        page = library.catalogue()
        assert "2 document(s)" in page
        assert "plan: 2 word(s)" in page
        assert "notes: 3 word(s)" in page


class TestLibrarySync:
    def test_shared_docs_shake_and_lonely_ones_are_named(
        self,
    ):
        mine = stocked()
        theirs = Library(site="bob")
        theirs.open_doc("plan")
        theirs.type_in("plan", 0, "or wednesday ")
        theirs.open_doc("secrets")
        page = sync_libraries(mine, theirs)
        assert "plan: settled in" in page
        assert (
            mine.docs["plan"].text()
            == theirs.docs["plan"].text()
        )
        assert (
            "notes: only on alice's shelves" in page
        )
        assert (
            "secrets: only on bob's shelves" in page
        )

    def test_two_empty_libraries_reconcile_nothing(self):
        assert "nothing to reconcile" in (
            sync_libraries(
                Library(site="alice"),
                Library(site="bob"),
            )
        )
