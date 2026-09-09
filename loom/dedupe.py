"""Dedupe: remove the adjacent duplicate lines a paste left, as operations.

The repeats module finds duplicated lines; this removes them,
but only the ones worth removing: a non-blank line identical
to the line immediately above it, the signature of a paste
that landed twice. It removes exactly those, expressed as a
patch so the surviving copy keeps its strands and only the
redundant lines and their newlines are sheared, and it
converges across replicas the way a patch does. The
restraint to adjacent duplicates is deliberate and stated. A
line that repeats far from its twin is usually meant, a
refrain, a repeated table header, a heading that recurs by
design, and deleting those would be editing the writer's
content rather than cleaning a mechanical slip. Blank lines
are never treated as duplicates either, because a run of
blank lines is spacing a writer chose, not an accident, and
collapsing it would reflow the document under the guise of
tidying. So dedupe stays narrow on purpose, fixing the one
error it can be sure about, the consecutive identical line,
and leaving every judgement call to the writer, since a
cleaner that guessed at intent would eventually guess wrong
about text nobody wanted touched.
"""

from __future__ import annotations

from loom.author import Author
from loom.patch import patch
from loom.weave import Op


def _deduped(text: str) -> str:
    out: list[str] = []
    for line in text.split("\n"):
        if out and line == out[-1] and line.strip():
            continue
        out.append(line)
    return "\n".join(out)


def dedupe_lines(author: Author) -> list[Op]:
    return patch(author, _deduped(author.text()))


def deduped_text(text: str) -> str:
    return _deduped(text)
