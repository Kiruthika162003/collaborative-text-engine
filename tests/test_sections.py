from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.errors import Invalid, Missing
from loom.sections import move_section
from loom.transcript import Tape


def three_sections() -> Author:
    author = Author(site="alice")
    author.type_at(
        0, "# A\nalpha\n# B\nbeta\n# C\ngamma"
    )
    return author


class TestMoving:
    def test_a_section_moves_before_another(self):
        author = three_sections()
        move_section(author, "C", before="B")
        assert author.text() == (
            "# A\nalpha\n# C\ngamma\n# B\nbeta\n"
        )

    def test_a_section_moves_to_the_end(self):
        author = three_sections()
        move_section(author, "A", before=None)
        assert author.text() == (
            "# B\nbeta\n# C\ngamma\n# A\nalpha"
        )

    def test_a_section_cannot_move_inside_itself(self):
        author = three_sections()
        with pytest.raises(Invalid):
            move_section(author, "B", before="B")

    def test_an_unknown_section_is_refused(self):
        author = three_sections()
        with pytest.raises(Missing):
            move_section(author, "Z", before="A")


class TestHonesty:
    def test_moved_text_gets_new_strand_ids(self):
        author = three_sections()
        before_ids = {
            s.id
            for s in author.weave.strands
            if not s.sheared
        }
        move_section(author, "C", before="A")
        gamma_strands = [
            s
            for s in author.weave.strands
            if not s.sheared and s.glyph == "g"
        ]
        assert any(
            s.id not in before_ids
            for s in gamma_strands
        )

    def test_the_move_converges_on_a_peer(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(
                0, "# A\nx\n# B\ny"
            ),
        )
        circle.settle()
        alice = circle.author("alice")
        alice.tape = Tape()
        move_section(alice, "B", before="A")
        circle.say("alice", alice.tape.reel)
        circle.settle()
        assert circle.converged() == (
            "# B\ny\n# A\nx\n"
        )
