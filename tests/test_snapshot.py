from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.errors import Torn
from loom.snapshot import (
    cloth_digest,
    freeze,
    same_fabric,
    thaw,
)


def edited_author() -> Author:
    author = Author(site="alice")
    author.type_at(0, "hello world")
    author.erase_at(5, 1)
    author.type_at(5, "|")
    return author


class TestRoundTrips:
    def test_the_fabric_survives_freezing(self):
        author = edited_author()
        rebuilt = thaw(freeze(author.weave))
        assert rebuilt.text() == author.text()
        assert same_fabric(rebuilt, author.weave)
        assert rebuilt.tombstone_count() == (
            author.weave.tombstone_count()
        )

    def test_the_index_is_rebuilt_not_trusted(self):
        author = edited_author()
        rebuilt = thaw(freeze(author.weave))
        for op_id, index in rebuilt.by_id.items():
            assert rebuilt.strands[index].id == op_id

    def test_a_thawed_fabric_still_weaves(self):
        author = edited_author()
        rebuilt = thaw(freeze(author.weave))
        resumed = Author(site="alice", weave=rebuilt)
        for op_id in rebuilt.by_id:
            resumed.clock.seen[op_id.site] = max(
                resumed.clock.seen.get(op_id.site, 0),
                op_id.counter,
            )
        resumed.witness_rank = 20
        resumed.type_at(0, "> ")
        assert resumed.text().startswith("> hello")


class TestTornPages:
    def test_the_header_word_is_law(self):
        with pytest.raises(Torn):
            thaw("notasnap|0")

    def test_truncation_is_caught_by_count(self):
        author = edited_author()
        page = freeze(author.weave)
        truncated = "\n".join(
            page.split("\n")[:-1]
        )
        with pytest.raises(Torn) as caught:
            thaw(truncated)
        assert "full disks truncate" in str(
            caught.value
        )

    def test_a_third_state_is_refused(self):
        page = "loomsnap|1\nalice:1|^|1|?|a"
        with pytest.raises(Torn) as caught:
            thaw(page)
        assert "nothing third" in str(caught.value)

    def test_a_doubled_strand_is_refused(self):
        page = (
            "loomsnap|2\n"
            "alice:1|^|1|.|a\n"
            "alice:1|^|1|.|a"
        )
        with pytest.raises(Torn) as caught:
            thaw(page)
        assert "one id, one strand" in str(caught.value)


class TestTheTwoOaths:
    def test_converged_circles_share_a_fabric_digest(
        self,
    ):
        circle = Circle.of(
            ["alice", "bob"],
            temperament="tides",
            seed=9,
        )
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "abc"),
        )
        circle.say(
            "bob",
            circle.author("bob").type_at(0, "xyz"),
        )
        circle.settle()
        circle.converged()
        assert same_fabric(
            circle.author("alice").weave,
            circle.author("bob").weave,
        )

    def test_the_cloth_oath_is_weaker_on_purpose(self):
        plain = Author(site="alice")
        plain.type_at(0, "same")
        scarred = Author(site="bob")
        scarred.type_at(0, "sameX")
        scarred.erase_at(4, 1)
        assert cloth_digest(plain.weave) == (
            cloth_digest(scarred.weave)
        )
        assert not same_fabric(
            plain.weave, scarred.weave
        )
