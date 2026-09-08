"""Chunks: a big fabric snapshotted in pieces that verify one at a time.

A whole-fabric snapshot is one line per strand and one
digest over all of it, which is fine until the document is
a novel and the snapshot is a file a network ships in
pieces. Chunking splits the frozen snapshot into fixed-size
runs of strands, each piece carrying its own digest and its
ordinal out of the total, so a corrupted or missing piece
is named precisely rather than failing the whole load with
a shrug. Reassembly checks three things a partial transfer
gets wrong: every ordinal present exactly once, each
piece's own digest, and the count matching the manifest,
and only a set that passes all three thaws, because a
snapshot rebuilt from pieces nobody verified is a snapshot
that lies with extra steps. The manifest is a separate
small object listing the piece digests, the thing a
receiver fetches first to know what it is collecting, and
the whole scheme reduces to the plain snapshot when the
fabric fits in one chunk, a special case the code does not
special-case.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from loom.errors import Torn
from loom.snapshot import freeze, thaw
from loom.weave import Weave

DEFAULT_CHUNK = 64


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


@dataclass(frozen=True)
class Chunk:
    ordinal: int
    total: int
    digest: str
    body: str


@dataclass
class Manifest:
    total: int
    digests: list[str] = field(default_factory=list)

    def matches(self, chunk: Chunk) -> bool:
        return (
            chunk.ordinal < self.total
            and self.digests[chunk.ordinal]
            == chunk.digest
        )


def split(
    weave: Weave, chunk_size: int = DEFAULT_CHUNK
) -> tuple[list[Chunk], Manifest]:
    if chunk_size < 1:
        raise Torn(
            "a chunk size below one slices nothing "
            "into infinitely many pieces"
        )
    page = freeze(weave)
    lines = page.split("\n")
    header, body_lines = lines[0], lines[1:]
    chunks: list[Chunk] = []
    groups = [
        body_lines[i : i + chunk_size]
        for i in range(0, len(body_lines), chunk_size)
    ] or [[]]
    total = len(groups)
    for ordinal, group in enumerate(groups):
        payload = "\n".join(group)
        stored = (
            f"{header}\n{payload}"
            if ordinal == 0
            else payload
        )
        chunks.append(
            Chunk(
                ordinal=ordinal,
                total=total,
                digest=_digest(stored),
                body=stored,
            )
        )
    manifest = Manifest(
        total=total,
        digests=[c.digest for c in chunks],
    )
    return chunks, manifest


def reassemble(
    chunks: list[Chunk], manifest: Manifest
) -> Weave:
    if len(chunks) != manifest.total:
        raise Torn(
            f"the manifest expects {manifest.total} "
            f"piece(s) and {len(chunks)} arrived; a "
            "partial transfer names itself here"
        )
    ordinals = sorted(c.ordinal for c in chunks)
    if ordinals != list(range(manifest.total)):
        raise Torn(
            "the pieces are not a clean run of "
            "ordinals; one is missing or one is "
            "twinned"
        )
    ordered = sorted(chunks, key=lambda c: c.ordinal)
    for chunk in ordered:
        if _digest(chunk.body) != chunk.digest:
            raise Torn(
                f"piece {chunk.ordinal} fails its own "
                "digest; corruption named, not "
                "swallowed"
            )
        if not manifest.matches(chunk):
            raise Torn(
                f"piece {chunk.ordinal} does not match "
                "the manifest it claims to belong to"
            )
    body = "\n".join(chunk.body for chunk in ordered)
    return thaw(body)
