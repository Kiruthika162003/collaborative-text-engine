"""Whitespace: trim and squeeze the invisible glyphs without disturbing the visible ones.

Trailing spaces and doubled spaces are the lint of
collaborative prose, arriving from a dozen keyboards and
paste buffers, and cleaning them is shearing whitespace
strands, never touching a visible glyph or an anchor riding
one. Two operations, each careful about a different edge.
Trimming removes whitespace that sits at the end of a line,
the run between the last real glyph and the newline, and
the run at the very end of the document, the whitespace no
reader can see and every diff tool complains about.
Squeezing collapses an internal run of spaces to one, the
double space that crept between two words, but it spares
leading indentation on purpose, because the spaces at the
head of a line are structure, not noise, and a squeeze that
flattened indentation would turn a formatted list into a
paragraph in the name of tidiness. Both work by resolving
the exact strands to shear and then removing them, so a
concurrent edit landing between two of the doomed spaces
survives, and both leave a single space or a single newline
standing where a human would, because the goal is text a
person would have typed, not text stripped of every breath.
"""

from __future__ import annotations

from loom.author import Author
from loom.ids import OpId
from loom.weave import Op, Weave


def _visible(weave: Weave) -> list[tuple[OpId, str]]:
    return [
        (strand.id, strand.glyph)
        for strand in weave.strands
        if not strand.sheared
    ]


def _shear_ids(author: Author, ids: list[OpId]) -> list[Op]:
    ops: list[Op] = []
    for strand_id in ids:
        position = author.weave.by_id[strand_id]
        visible = sum(
            1 for strand in author.weave.strands[:position] if not strand.sheared
        )
        ops.extend(author.erase_at(visible, 1))
    return ops


def _is_trailing(seq: list[tuple[OpId, str]], index: int) -> bool:
    for after in range(index, len(seq)):
        glyph = seq[after][1]
        if glyph == "\n":
            return True
        if glyph not in " \t":
            return False
    return True


def trim_trailing(author: Author) -> list[Op]:
    seq = _visible(author.weave)
    doomed = [
        seq[index][0]
        for index in range(len(seq))
        if seq[index][1] in " \t" and _is_trailing(seq, index)
    ]
    return _shear_ids(author, doomed)


def squeeze_spaces(author: Author) -> list[Op]:
    seq = _visible(author.weave)
    doomed: list[OpId] = []
    index = 0
    while index < len(seq):
        if seq[index][1] != " ":
            index += 1
            continue
        run_start = index
        while index < len(seq) and seq[index][1] == " ":
            index += 1
        before = seq[run_start - 1][1] if run_start > 0 else "\n"
        run_length = index - run_start
        if run_length >= 2 and before != "\n":
            doomed.extend(
                seq[keep][0] for keep in range(run_start + 1, index)
            )
    return _shear_ids(author, doomed)
