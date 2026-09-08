from __future__ import annotations

from loom.author import Author
from loom.spellwatch import Spellwatch


def watched() -> tuple[Author, Spellwatch]:
    author = Author(site="alice")
    author.type_at(0, "the qwik brown fox")
    return author, Spellwatch(
        lexicon={"the", "brown", "fox"}
    )


class TestDoubting:
    def test_absent_words_are_doubted(self):
        author, watch = watched()
        found = watch.doubts(author.weave)
        assert [d.word for d in found] == ["qwik"]

    def test_known_words_pass(self):
        author = Author(site="alice")
        author.type_at(0, "the fox")
        watch = Spellwatch(lexicon={"the", "fox"})
        assert watch.doubts(author.weave) == []

    def test_identifiers_are_skipped(self):
        author = Author(site="alice")
        author.type_at(0, "config v2 and h2o")
        watch = Spellwatch(lexicon={"config", "and"})
        assert watch.doubts(author.weave) == []

    def test_the_report_lists_the_doubts(self):
        author, watch = watched()
        page = watch.report(author.weave)
        assert "1 word(s) doubted: qwik" in page
        assert "checked, not graded" in page


class TestPins:
    def test_a_doubt_survives_upstream_typing(self):
        author, watch = watched()
        doubt = watch.doubts(author.weave)[0]
        author.type_at(0, ">>> ")
        assert watch.still_doubted(author.weave, doubt)

    def test_fixing_the_word_clears_the_doubt(self):
        author = Author(site="alice")
        author.type_at(0, "the qwik brown fox")
        watch = Spellwatch(
            lexicon={"the", "brown", "fox", "quick"}
        )
        doubt = watch.doubts(author.weave)[0]
        author.erase_at(4, 4)
        author.type_at(4, "quick")
        assert not watch.still_doubted(
            author.weave, doubt
        )
        assert watch.doubts(author.weave) == []

    def test_a_clean_document_says_so(self):
        author = Author(site="alice")
        author.type_at(0, "all good words")
        watch = Spellwatch(
            lexicon={"all", "good", "words"}
        )
        assert "no words doubted" in watch.report(
            author.weave
        )
