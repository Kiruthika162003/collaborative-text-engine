from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.mdlint import clean
from loom.tidy import tidy

MESSY = "# T  \n\n\n* a  \n+ b\n\n1. x\n3. y"


class TestTidy:
    def test_tidy_cleans_a_messy_document(self):
        author = Author(site="alice")
        author.type_at(0, MESSY)
        tidy(author)
        assert author.text() == "# T\n\n- a\n- b\n\n1. x\n2. y"

    def test_tidy_leaves_a_clean_document_alone(self):
        author = Author(site="alice")
        author.type_at(0, "# Title\n\n- a\n- b\n")
        assert tidy(author) == []

    def test_tidy_is_idempotent(self):
        author = Author(site="alice")
        author.type_at(0, MESSY)
        tidy(author)
        assert tidy(author) == []

    def test_the_tidied_document_passes_the_safe_rules(self):
        author = Author(site="alice")
        author.type_at(0, MESSY)
        tidy(author)
        assert clean(author)


class TestScope:
    def test_a_heading_level_skip_is_left_for_the_writer(self):
        author = Author(site="alice")
        author.type_at(0, "# A\n### C")
        tidy(author)
        assert author.text() == "# A\n### C"


class TestConvergence:
    def test_tidy_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice", circle.author("alice").type_at(0, "* a  \n+ b")
        )
        circle.settle()
        circle.say("alice", tidy(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "- a\n- b"
