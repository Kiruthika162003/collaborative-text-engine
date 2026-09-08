from __future__ import annotations

from loom.author import Author
from loom.frontmatter import body, get, parse, report

DOC = (
    "---\n"
    "title: My Note\n"
    "author: alice\n"
    "---\n"
    "The body starts here."
)


class TestParse:
    def test_fields_are_read_from_the_top_block(self):
        author = Author(site="alice")
        author.type_at(0, DOC)
        matter = parse(author.weave)
        assert matter.present
        assert matter.fields == {"title": "My Note", "author": "alice"}

    def test_the_body_line_points_past_the_block(self):
        author = Author(site="alice")
        author.type_at(0, DOC)
        assert body(author.weave) == "The body starts here."

    def test_get_reads_one_field(self):
        author = Author(site="alice")
        author.type_at(0, DOC)
        assert get(author.weave, "title") == "My Note"
        assert get(author.weave, "missing", "fallback") == "fallback"


class TestPosition:
    def test_a_middle_dash_line_is_not_front_matter(self):
        author = Author(site="alice")
        author.type_at(0, "body first\n---\nnot: metadata")
        assert not parse(author.weave).present

    def test_an_unclosed_block_is_not_front_matter(self):
        author = Author(site="alice")
        author.type_at(0, "---\ntitle: open\nno closing dash")
        matter = parse(author.weave)
        assert not matter.present
        assert body(author.weave) == author.text()


class TestMalformed:
    def test_a_colonless_line_is_kept_aside(self):
        author = Author(site="alice")
        author.type_at(0, "---\ntitle: ok\njust a stray line\n---\nbody")
        matter = parse(author.weave)
        assert matter.fields == {"title": "ok"}
        assert matter.malformed == ["just a stray line"]


class TestReport:
    def test_the_report_lists_fields(self):
        author = Author(site="alice")
        author.type_at(0, DOC)
        page = report(author.weave)
        assert "2 field(s)" in page
        assert "title: My Note" in page

    def test_a_plain_document_reports_no_front_matter(self):
        author = Author(site="alice")
        author.type_at(0, "just a body")
        assert "starts with its body" in report(author.weave)
