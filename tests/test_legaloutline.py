from __future__ import annotations

from loom.author import Author
from loom.legaloutline import label_for, outline_labels, render


class TestLabelFor:
    def test_the_style_cycles_by_depth(self):
        assert label_for(1, 1) == "I"
        assert label_for(2, 1) == "A"
        assert label_for(3, 1) == "1"
        assert label_for(4, 1) == "a"
        assert label_for(5, 1) == "i"

    def test_letters_roll_over_past_z(self):
        assert label_for(2, 26) == "Z"
        assert label_for(2, 27) == "AA"

    def test_roman_counts_up(self):
        assert label_for(1, 4) == "IV"


class TestOutline:
    def test_labels_follow_depth_and_position(self):
        author = Author(site="alice")
        author.type_at(0, "# One\n# Two\n## Sub\n### Deep")
        labels = dict(outline_labels(author.weave))
        assert labels["One"] == "I"
        assert labels["Two"] == "II"
        assert labels["Sub"] == "A"
        assert labels["Deep"] == "1"

    def test_subsections_restart_under_each_section(self):
        author = Author(site="alice")
        author.type_at(0, "# One\n## A1\n# Two\n## B1")
        labels = dict(outline_labels(author.weave))
        assert labels["A1"] == "A"
        assert labels["B1"] == "A"


class TestRender:
    def test_render_indents_by_depth(self):
        author = Author(site="alice")
        author.type_at(0, "# Top\n## Sub")
        page = render(author.weave)
        assert "I. Top" in page
        assert "  A. Sub" in page

    def test_a_flat_document_has_no_outline(self):
        author = Author(site="alice")
        author.type_at(0, "no headings")
        assert "no headings" in render(author.weave)
