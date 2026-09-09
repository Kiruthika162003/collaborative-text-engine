from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.linkify import autolink, would_link


class TestAutolink:
    def test_a_bare_url_is_wrapped(self):
        author = Author(site="alice")
        author.type_at(0, "visit http://example.com today")
        autolink(author)
        assert author.text() == "visit <http://example.com> today"

    def test_trailing_punctuation_stays_outside_the_link(self):
        author = Author(site="alice")
        author.type_at(0, "see http://x.org.")
        autolink(author)
        assert author.text() == "see <http://x.org>."

    def test_two_urls_are_both_wrapped(self):
        author = Author(site="alice")
        author.type_at(0, "http://a.com and http://b.com")
        autolink(author)
        assert author.text() == "<http://a.com> and <http://b.com>"


class TestSkips:
    def test_an_already_autolinked_url_is_left_alone(self):
        author = Author(site="alice")
        author.type_at(0, "go <http://x.com> now")
        assert autolink(author) == []

    def test_a_markdown_link_target_is_left_alone(self):
        author = Author(site="alice")
        author.type_at(0, "see [x](http://y.com)")
        assert autolink(author) == []

    def test_prose_without_urls_links_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "no urls here")
        assert would_link(author.text()) == 0


class TestConvergence:
    def test_autolink_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "at http://site.com end"),
        )
        circle.settle()
        circle.say("alice", autolink(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert "<http://site.com>" in circle.converged()
