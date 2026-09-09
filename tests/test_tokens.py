from __future__ import annotations

from loom.tokens import counts, numbers, render, tokenize, words


class TestTokenize:
    def test_a_contraction_is_one_word(self):
        assert words("don't stop") == ["don't", "stop"]

    def test_a_decimal_is_one_number(self):
        assert numbers("pi is 3.14 today") == ["3.14"]

    def test_a_hyphen_splits_a_pair(self):
        assert words("a-b") == ["a", "b"]

    def test_whitespace_runs_are_one_token(self):
        found = [t for t in tokenize("a   b") if t.kind == "space"]
        assert len(found) == 1


class TestCoverage:
    def test_the_tokens_tile_the_text(self):
        text = "one, 2 three-four! done_"
        total = sum(len(t.text) for t in tokenize(text))
        assert total == len(text)

    def test_every_character_has_a_kind(self):
        text = "x_9 ~ é"
        assert all(
            t.kind in {"word", "number", "space", "symbol"}
            for t in tokenize(text)
        )


class TestCounts:
    def test_counts_tally_by_kind(self):
        tally = counts("a b 1")
        assert tally["word"] == 2
        assert tally["number"] == 1
        assert tally["space"] == 2


class TestRender:
    def test_render_labels_each_token(self):
        page = render("hi 5")
        assert "word:'hi'" in page
        assert "number:'5'" in page

    def test_empty_text_has_no_tokens(self):
        assert "no tokens" in render("")
