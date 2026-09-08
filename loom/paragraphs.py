"""Paragraphs: the cloth grouped into blocks, each block pinned to a strand.

Documents are read in paragraphs, and this module groups
the visible cloth into blocks split on blank lines, the
same convention every plain-text writer already uses, so
the structure is discovered rather than imposed. Each
block is pinned to the id of its first strand, which makes
a paragraph reference survive edits the way a caret does:
text inserted above shifts the block's number but not its
pin, and a reader who bookmarked paragraph three by pin
still finds their paragraph after someone adds two above
it. Empty blocks between doubled blank lines are dropped
from the count because nobody means the void between
paragraphs as a paragraph, and the block a strand belongs
to is answered by walking to its pin, currently being the
honest tense since paragraphs, like everything visible,
are weather. The outline names each block by its first
few words, which is how writers find the paragraph they
mean without reading all of them.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.errors import Missing
from loom.ids import OpId
from loom.weave import Weave


@dataclass(frozen=True)
class Block:
    pin: OpId
    text: str
    ordinal: int


def blocks(weave: Weave) -> list[Block]:
    found: list[Block] = []
    current_glyphs: list[str] = []
    current_pin: OpId | None = None
    blank_run = 0
    ordinal = 0

    def flush() -> None:
        nonlocal current_pin
        if current_pin is not None and current_glyphs:
            nonlocal ordinal
            found.append(
                Block(
                    pin=current_pin,
                    text="".join(current_glyphs),
                    ordinal=ordinal,
                )
            )
            ordinal += 1
        current_glyphs.clear()
        current_pin = None

    for strand in weave.strands:
        if strand.sheared:
            continue
        if strand.glyph == "\n":
            blank_run += 1
            if blank_run >= 2:
                flush()
            continue
        if blank_run == 1 and current_glyphs:
            current_glyphs.append(" ")
        blank_run = 0
        if current_pin is None:
            current_pin = strand.id
        current_glyphs.append(strand.glyph)
    flush()
    return found


def block_count(weave: Weave) -> int:
    return len(blocks(weave))


def block_of(weave: Weave, strand_id: OpId) -> int:
    target = weave.by_id.get(strand_id)
    if target is None:
        raise Missing(
            f"{strand_id.wire()} is not in the fabric"
        )
    for block in blocks(weave):
        pin_pos = weave.by_id[block.pin]
        if pin_pos <= target:
            candidate = block.ordinal
        else:
            return candidate
    return blocks(weave)[-1].ordinal


def outline(weave: Weave) -> str:
    held = blocks(weave)
    if not held:
        return "no paragraphs; the cloth is blank"
    lines = [f"{len(held)} paragraph(s):"]
    for block in held:
        head = block.text[:32]
        if len(block.text) > 32:
            head += "..."
        lines.append(f"  {block.ordinal}: {head!r}")
    return "\n".join(lines)
