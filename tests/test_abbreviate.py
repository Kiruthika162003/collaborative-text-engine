from __future__ import annotations

from loom.abbreviate import expand, expand_ops, would_expand
from loom.author import Author
from loom.circle import Circle

GLOSSARY = {"btw": "by the way", "eg": "for example"}


class TestExpand:
    def test_an_abbreviation_expands(self):
        assert expand("btw i agree", GLOSSARY) == "by the way i agree"

    def test_matching_is_case_insensitive(self):
        assert expand("BTW hello", GLOSSARY) == "by the way hello"

    def test_a_match_inside_a_word_is_left_alone(self):
        assert expand("btworld", GLOSSARY) == "btworld"

    def test_the_longer_abbreviation_wins(self):
        assert expand("eg here", {"e": "X", "eg": "for example"}) == (
            "for example here"
        )


class TestOps:
    def test_expansion_reaches_the_text(self):
        author = Author(site="alice")
        author.type_at(0, "see eg this")
        expand_ops(author, GLOSSARY)
        assert author.text() == "see for example this"

    def test_a_document_without_abbreviations_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "plain prose")
        assert expand_ops(author, GLOSSARY) == []


class TestQuery:
    def test_would_expand_detects_a_match(self):
        assert would_expand("btw", GLOSSARY)
        assert not would_expand("nothing here", GLOSSARY)


class TestConvergence:
    def test_expansion_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice", circle.author("alice").type_at(0, "btw done")
        )
        circle.settle()
        circle.say("alice", expand_ops(circle.author("alice"), GLOSSARY))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "by the way done"
