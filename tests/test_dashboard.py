from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.dashboard import balance, page
from loom.transcript import Tape


def solo() -> tuple[Author, Tape]:
    tape = Tape()
    author = Author(site="alice", tape=tape)
    author.type_at(0, "the quick brown fox jumps over")
    return author, tape


def duo() -> Circle:
    circle = Circle.of(["alice", "bob"])
    circle.say(
        "alice",
        circle.author("alice").type_at(0, "alice writes half "),
    )
    circle.settle()
    circle.say(
        "bob",
        circle.author("bob").type_at(
            circle.author("bob").weave.visible_count(),
            "and bob writes half",
        ),
    )
    circle.settle()
    return circle


class TestBalance:
    def test_a_lone_author_holds_the_whole_hundred(self):
        author, _tape = solo()
        assert balance(author.weave) == 100

    def test_an_empty_page_has_no_busiest_hand(self):
        author = Author(site="alice")
        assert balance(author.weave) == 0

    def test_a_shared_page_splits_below_a_hundred(self):
        circle = duo()
        assert balance(circle.author("alice").weave) < 100


class TestPage:
    def test_a_solo_document_reads_as_a_monologue(self):
        author, tape = solo()
        rendered = page(author.weave, tape)
        assert "monologue" in rendered

    def test_a_shared_document_reads_as_a_conversation(self):
        circle = duo()
        rendered = page(
            circle.author("alice").weave,
            Tape(),
        )
        assert "conversation" in rendered

    def test_the_page_names_its_size_in_words(self):
        author, tape = solo()
        rendered = page(author.weave, tape)
        assert "6 word(s)" in rendered

    def test_an_empty_page_owes_nobody(self):
        author = Author(site="alice")
        rendered = page(author.weave, Tape())
        assert "owes nobody" in rendered

    def test_the_dashboard_prescribes_nothing(self):
        author, tape = solo()
        rendered = page(author.weave, tape)
        assert "prescribes nothing" in rendered

    def test_the_rhythm_line_counts_handoffs(self):
        author, tape = solo()
        rendered = page(author.weave, tape)
        assert "handoff(s)" in rendered
