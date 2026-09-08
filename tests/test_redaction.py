from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Missing
from loom.ids import OpId
from loom.mailroom import Mailroom
from loom.redaction import (
    BLOCK,
    Redact,
    Redactor,
    redact_range,
)


def secretive() -> tuple[Author, Redactor]:
    author = Author(site="alice")
    author.type_at(0, "user password=hunter2 end")
    return author, Redactor(weave=author.weave)


class TestScrubbing:
    def test_the_content_is_gone_not_hidden(self):
        author, red = secretive()
        redact_range(
            author.weave,
            red,
            OpId(site="admin", counter=1),
            14,
            7,
        )
        assert "hunter2" not in author.text()
        joined = "".join(
            s.glyph for s in author.weave.strands
        )
        assert "hunter2" not in joined

    def test_the_structure_stays_intact(self):
        author, red = secretive()
        before = len(author.weave.strands)
        redact_range(
            author.weave,
            red,
            OpId(site="admin", counter=1),
            14,
            7,
        )
        assert len(author.weave.strands) == before
        assert len(author.text()) == 25
        assert author.text().count(BLOCK) == 7

    def test_redaction_is_idempotent(self):
        author, red = secretive()
        redaction = Redact(
            id=OpId(site="admin", counter=1),
            targets=(
                author.weave.strand_at_visible(14).id,
            ),
        )
        red.redact(redaction)
        receipt = red.redact(redaction)
        assert "already applied" in receipt

    def test_an_unseen_target_buffers(self):
        _author, red = secretive()
        with pytest.raises(Missing):
            red.redact(
                Redact(
                    id=OpId(site="admin", counter=2),
                    targets=(
                        OpId(site="zed", counter=9),
                    ),
                )
            )


class TestConvergence:
    def test_a_redaction_scrubs_every_replica(self):
        alice = Author(site="alice")
        ops = alice.type_at(0, "user password=hunter2 end")
        bob = Author(site="bob")
        room = Mailroom(author=bob)
        for op in ops:
            room.receive(op)
        bob_red = Redactor(weave=bob.weave)
        targets = tuple(
            bob.weave.strand_at_visible(14 + off).id
            for off in range(7)
        )
        redaction = Redact(
            id=OpId(site="admin", counter=1),
            targets=targets,
        )
        bob_red.redact(redaction)
        assert "hunter2" not in bob.text()
        assert bob_red.redacted_count() == 7
