from __future__ import annotations

from loom.worddiff import render, summary, tokenize, word_diff


class TestTokenizing:
    def test_whitespace_is_its_own_token(self):
        assert tokenize("a  b") == ["a", "  ", "b"]

    def test_a_paragraph_break_is_a_token(self):
        assert "\n\n" in tokenize("one\n\ntwo")


class TestDiffing:
    def test_a_swap_reads_like_an_editors_note(self):
        page = render(
            "the quick brown fox",
            "the swift brown fox",
        )
        assert page == (
            "the [-quick-][+swift+] brown fox"
        )

    def test_additions_keep_their_spacing(self):
        page = render(
            "the quick brown fox",
            "the swift brown fox jumps",
        )
        assert page == (
            "the [-quick-][+swift+] brown fox "
            "[+jumps+]"
        )

    def test_identical_texts_show_no_marks(self):
        page = render("a b c", "a b c")
        assert page == "a b c"
        assert "[" not in page

    def test_a_collapsed_break_is_visible(self):
        spans = word_diff("one\n\ntwo", "one two")
        verbs = {
            s.verb
            for s in spans
            if not s.text.strip()
        }
        assert "dropped" in verbs
        assert "added" in verbs


class TestSummary:
    def test_the_three_verbs_are_counted(self):
        counts = summary(
            "the quick brown fox",
            "the swift brown fox jumps",
        )
        assert counts["kept"] == 3
        assert counts["dropped"] == 1
        assert counts["added"] == 2

    def test_similarity_sorts_never_grades(self):
        near = summary("a b c d", "a b c e")
        far = summary("a b c d", "w x y z")
        assert near["similarity"] > far["similarity"]

    def test_identical_texts_are_wholly_similar(self):
        assert summary("same", "same")[
            "similarity"
        ] == 1.0
