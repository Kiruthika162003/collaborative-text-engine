from __future__ import annotations

import pytest

from loom.author import Author
from loom.chunks import Chunk, reassemble, split
from loom.errors import Torn
from loom.snapshot import same_fabric


def big_author() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "".join(
            chr(97 + i % 26) for i in range(200)
        ),
    )
    author.erase_at(10, 5)
    return author


class TestSplitting:
    def test_pieces_reassemble_to_the_same_fabric(self):
        author = big_author()
        chunks, manifest = split(
            author.weave, chunk_size=40
        )
        assert len(chunks) == 5
        rebuilt = reassemble(chunks, manifest)
        assert same_fabric(rebuilt, author.weave)
        assert rebuilt.text() == author.text()

    def test_each_piece_carries_its_ordinal(self):
        author = big_author()
        chunks, _manifest = split(
            author.weave, chunk_size=40
        )
        assert [c.ordinal for c in chunks] == [
            0,
            1,
            2,
            3,
            4,
        ]
        assert all(
            c.total == 5 for c in chunks
        )

    def test_the_scheme_reduces_to_one_chunk(self):
        author = big_author()
        chunks, manifest = split(
            author.weave, chunk_size=10000
        )
        assert len(chunks) == 1
        assert same_fabric(
            reassemble(chunks, manifest), author.weave
        )

    def test_a_zero_chunk_size_is_torn(self):
        author = big_author()
        with pytest.raises(Torn):
            split(author.weave, chunk_size=0)


class TestReassembly:
    def test_a_missing_piece_is_named(self):
        author = big_author()
        chunks, manifest = split(
            author.weave, chunk_size=40
        )
        with pytest.raises(Torn) as caught:
            reassemble(chunks[:-1], manifest)
        assert "partial transfer names itself" in str(
            caught.value
        )

    def test_a_twinned_ordinal_is_named(self):
        author = big_author()
        chunks, manifest = split(
            author.weave, chunk_size=40
        )
        doubled = [*chunks[:-1], chunks[0]]
        with pytest.raises(Torn) as caught:
            reassemble(doubled, manifest)
        assert "missing or one is twinned" in str(
            caught.value
        )

    def test_a_corrupted_body_fails_its_digest(self):
        author = big_author()
        chunks, manifest = split(
            author.weave, chunk_size=40
        )
        tampered = list(chunks)
        victim = tampered[2]
        tampered[2] = Chunk(
            ordinal=victim.ordinal,
            total=victim.total,
            digest=victim.digest,
            body=victim.body + "|garbage",
        )
        with pytest.raises(Torn) as caught:
            reassemble(tampered, manifest)
        assert "fails its own digest" in str(
            caught.value
        )
