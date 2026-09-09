from __future__ import annotations

from loom.htmlpage import page, title_of


class TestTitle:
    def test_the_title_comes_from_the_first_heading(self):
        assert title_of("# My Page\n\nbody") == "My Page"

    def test_a_headingless_document_is_untitled(self):
        assert title_of("just prose") == "Untitled"


class TestPage:
    def test_the_page_has_a_doctype_and_shell(self):
        out = page("# Hi\n\nbody")
        assert out.startswith("<!doctype html>")
        assert "<html>" in out
        assert "<body>" in out

    def test_the_title_is_set_from_the_heading(self):
        out = page("# Welcome\n\ntext")
        assert "<title>Welcome</title>" in out

    def test_an_explicit_title_overrides(self):
        out = page("# Ignored", title="Chosen")
        assert "<title>Chosen</title>" in out

    def test_the_title_is_escaped(self):
        out = page("# A & B")
        assert "<title>A &amp; B</title>" in out

    def test_the_body_is_the_rendered_markdown(self):
        out = page("# Hi\n\nsome body")
        assert "<h1>Hi</h1>" in out
        assert "<p>some body</p>" in out
