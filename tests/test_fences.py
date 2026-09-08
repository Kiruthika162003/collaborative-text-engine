from __future__ import annotations

from loom.author import Author
from loom.fences import (
    code_lines,
    fences,
    in_code,
    languages,
    report,
)

DOC = (
    "intro\n"
    "```python\n"
    "x = 1\n"
    "y = 2\n"
    "```\n"
    "outro"
)


class TestFinding:
    def test_a_fence_is_found_with_its_language(self):
        author = Author(site="alice")
        author.type_at(0, DOC)
        found = fences(author.weave)
        assert len(found) == 1
        assert found[0].language == "python"

    def test_the_body_is_taken_literally(self):
        author = Author(site="alice")
        author.type_at(0, DOC)
        assert fences(author.weave)[0].body == "x = 1\ny = 2"

    def test_a_fence_is_marked_closed(self):
        author = Author(site="alice")
        author.type_at(0, DOC)
        assert fences(author.weave)[0].closed


class TestUnclosed:
    def test_an_unclosed_fence_runs_to_the_end_and_is_flagged(self):
        author = Author(site="alice")
        author.type_at(0, "text\n```\nnever shut\nmore")
        found = fences(author.weave)
        assert len(found) == 1
        assert not found[0].closed
        assert found[0].close_line is None


class TestCodeLines:
    def test_body_lines_report_as_code(self):
        author = Author(site="alice")
        author.type_at(0, DOC)
        assert code_lines(author.weave) == {2, 3}

    def test_the_fence_delimiters_are_not_code_content(self):
        author = Author(site="alice")
        author.type_at(0, DOC)
        assert not in_code(author.weave, 1)
        assert in_code(author.weave, 2)

    def test_prose_lines_are_not_code(self):
        author = Author(site="alice")
        author.type_at(0, DOC)
        assert not in_code(author.weave, 0)


class TestReport:
    def test_languages_are_listed_once(self):
        author = Author(site="alice")
        author.type_at(
            0,
            "```py\na\n```\n```py\nb\n```\n```js\nc\n```",
        )
        assert languages(author.weave) == ["py", "js"]

    def test_a_prose_document_reports_no_fences(self):
        author = Author(site="alice")
        author.type_at(0, "just prose here")
        assert "all prose" in report(author.weave)

    def test_the_report_counts_unclosed(self):
        author = Author(site="alice")
        author.type_at(0, "```py\nx\n```\n```open\ny")
        assert "1 unclosed" in report(author.weave)
