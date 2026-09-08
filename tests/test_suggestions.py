from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Missing
from loom.ids import OpId
from loom.suggestions import SuggestionDesk


def draft_with_desk() -> tuple[Author, SuggestionDesk]:
    author = Author(site="alice")
    author.type_at(0, "the plain draft")
    return author, SuggestionDesk(weave=author.weave)


class TestSuggestingInserts:
    def test_the_two_views_split_on_a_suggestion(self):
        author, desk = draft_with_desk()
        ops = author.type_at(10, "bold ")
        for op in ops:
            desk.suggest_insert(op.id)
        assert desk.accepted_text() == "the plain draft"
        assert desk.suggested_text() == (
            "the plain bold draft"
        )

    def test_accepting_promotes_with_no_new_operation(
        self,
    ):
        author, desk = draft_with_desk()
        ops = author.type_at(10, "bold ")
        for op in ops:
            desk.suggest_insert(op.id)
        strands_before = len(author.weave.strands)
        for op in ops:
            desk.accept(op.id)
        assert len(author.weave.strands) == (
            strands_before
        )
        assert desk.accepted_text() == (
            "the plain bold draft"
        )

    def test_rejecting_shears_the_proposal(self):
        author, desk = draft_with_desk()
        ops = author.type_at(10, "bold ")
        for op in ops:
            desk.suggest_insert(op.id)
        for op in ops:
            desk.reject(op.id)
        assert desk.accepted_text() == "the plain draft"
        assert desk.suggested_text() == "the plain draft"

    def test_suggesting_a_stranger_is_refused(self):
        _author, desk = draft_with_desk()
        with pytest.raises(Missing):
            desk.suggest_insert(
                OpId(site="ghost", counter=9)
            )


class TestSuggestingDeletions:
    def test_a_suggested_deletion_hides_only_the_ask(
        self,
    ):
        author, desk = draft_with_desk()
        target = author.weave.strand_at_visible(4).id
        desk.suggest_deletion(
            OpId(site="bob", counter=1), target
        )
        assert desk.accepted_text() == "the plain draft"
        assert "p" not in desk.suggested_text()[4:5]

    def test_accepting_a_deletion_makes_it_real(self):
        author, desk = draft_with_desk()
        for index in range(4, 10):
            desk.suggest_deletion(
                OpId(site="bob", counter=index),
                author.weave.strand_at_visible(4).id,
            )
            break
        desk.accept(OpId(site="bob", counter=4))
        assert "the " in desk.accepted_text()

    def test_rejecting_a_deletion_keeps_the_glyph(self):
        author, desk = draft_with_desk()
        target = author.weave.strand_at_visible(4).id
        desk.suggest_deletion(
            OpId(site="bob", counter=1), target
        )
        desk.reject(OpId(site="bob", counter=1))
        assert desk.suggested_text() == "the plain draft"


class TestReview:
    def test_the_review_page_shows_both_views(self):
        author, desk = draft_with_desk()
        ops = author.type_at(15, " here")
        for op in ops:
            desk.suggest_insert(op.id)
        page = desk.review_page()
        assert "5 pending" in page
        assert "'the plain draft'" in page
        assert "'the plain draft here'" in page

    def test_no_suggestions_means_agreement(self):
        _author, desk = draft_with_desk()
        assert "the two views agree" in (
            desk.review_page()
        )
