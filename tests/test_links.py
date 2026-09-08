from __future__ import annotations

from loom.author import Author
from loom.links import catalogue, detect, still_valid


def linky() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "see https://loom.dev and mail a@b.co today",
    )
    return author


class TestDetection:
    def test_urls_and_emails_are_found(self):
        author = linky()
        found = detect(author.weave)
        kinds = {link.kind for link in found}
        assert kinds == {"url", "email"}
        texts = {link.text for link in found}
        assert "https://loom.dev" in texts
        assert "a@b.co" in texts

    def test_prose_with_dots_is_not_a_minefield(self):
        author = Author(site="alice")
        author.type_at(
            0, "end of sentence. start of another."
        )
        assert detect(author.weave) == []

    def test_a_link_needs_a_scheme(self):
        author = Author(site="alice")
        author.type_at(0, "visit loom.dev sometime")
        assert not any(
            link.kind == "url"
            for link in detect(author.weave)
        )


class TestPins:
    def test_a_link_survives_upstream_typing(self):
        author = linky()
        link = detect(author.weave)[0]
        author.type_at(0, ">>> ")
        assert still_valid(author.weave, link)

    def test_editing_the_link_makes_it_stale(self):
        author = linky()
        link = detect(author.weave)[0]
        author.erase_at(4, 5)
        assert not still_valid(author.weave, link)


class TestCatalogue:
    def test_the_catalogue_splits_by_kind(self):
        author = linky()
        page = catalogue(author.weave)
        assert "1 url(s), 1 email(s):" in page
        assert "url: https://loom.dev" in page
        assert "email: a@b.co" in page

    def test_pure_prose_has_no_links(self):
        author = Author(site="alice")
        author.type_at(0, "just words")
        assert "the cloth is all prose" in catalogue(
            author.weave
        )
