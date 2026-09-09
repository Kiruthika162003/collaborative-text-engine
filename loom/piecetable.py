"""Piece table: the text-editor buffer that never moves the characters it already holds.

A piece table represents an editable document as two flat
buffers and an ordered list of pieces that point into them. The
first buffer is the original text, loaded once and never
changed; the second is the add buffer, which only ever grows, as
every character anyone types is appended to its end and never
removed. A piece is a run of characters named by which buffer it
draws from, where in that buffer it starts, and how long it is,
and the document is the pieces read in order, each yielding its
slice of its buffer. This is what lets an edit touch only the
piece list: inserting text appends the typed characters to the
add buffer and drops a new piece into the list at the cursor,
splitting the piece the cursor sat inside into the part before
and the part after, and deleting a range drops the pieces it
covers and trims the ones at its ends, and in neither case does a
single character in either buffer move. I had guessed that
inserting into the middle of a piece would have to copy the tail
of that piece somewhere, the way splicing a string does; it does
not, and the whole reason the structure is worth its complexity
is that the split makes two pieces that point into the same
unmoved buffer, so an edit costs a few list entries no matter how
large the document or how far from the end the edit lands. The
price is that reading the document back means walking the pieces
and concatenating their slices, which the original naive string
does for free by already being contiguous, and that the add
buffer keeps every character ever typed even after it is deleted,
since deletion only unlinks the piece, so a long editing session
grows the add buffer without bound until the table is rebuilt.
That trade is the classic one an editor makes: cheap edits
anywhere against a text that is scattered across two buffers and
must be gathered to be read, which is the opposite of the naive
string's cheap read against edits that copy the whole tail.
"""

from __future__ import annotations

from loom.errors import Invalid

ORIGINAL = "original"
ADD = "add"


class Piece:
    __slots__ = ("buffer", "length", "start")

    def __init__(self, buffer: str, start: int, length: int) -> None:
        self.buffer = buffer
        self.start = start
        self.length = length

    def __repr__(self) -> str:
        return f"Piece({self.buffer}, {self.start}, {self.length})"


class PieceTable:
    def __init__(self, text: str = "") -> None:
        self._original = text
        self._add = ""
        self._pieces: list[Piece] = []
        if text:
            self._pieces.append(Piece(ORIGINAL, 0, len(text)))

    def _buffer(self, name: str) -> str:
        return self._original if name == ORIGINAL else self._add

    def __len__(self) -> int:
        return sum(piece.length for piece in self._pieces)

    def piece_count(self) -> int:
        return len(self._pieces)

    def text(self) -> str:
        return "".join(
            self._buffer(piece.buffer)[piece.start : piece.start + piece.length]
            for piece in self._pieces
        )

    def _split_at(self, offset: int) -> int:
        # Ensure a piece boundary sits exactly at offset, splitting a
        # piece if it straddles it, and return the index of the piece
        # that begins there (or the end index when offset is the length).
        if offset == 0:
            return 0
        running = 0
        for index, piece in enumerate(self._pieces):
            if running == offset:
                return index
            if running < offset < running + piece.length:
                left_length = offset - running
                left = Piece(piece.buffer, piece.start, left_length)
                right = Piece(
                    piece.buffer,
                    piece.start + left_length,
                    piece.length - left_length,
                )
                self._pieces[index : index + 1] = [left, right]
                return index + 1
            running += piece.length
        return len(self._pieces)

    def insert(self, offset: int, text: str) -> None:
        if not 0 <= offset <= len(self):
            raise Invalid(f"insert offset {offset} out of range")
        if text == "":
            return
        start = len(self._add)
        self._add += text
        index = self._split_at(offset)
        self._pieces.insert(index, Piece(ADD, start, len(text)))

    def delete(self, offset: int, length: int) -> None:
        if length < 0:
            raise Invalid("delete length is negative")
        if length == 0:
            return
        if not 0 <= offset <= len(self) - length:
            raise Invalid(f"delete range {offset}..{offset + length} out of bounds")
        start_index = self._split_at(offset)
        end_index = self._split_at(offset + length)
        del self._pieces[start_index:end_index]

    def replace(self, offset: int, length: int, text: str) -> None:
        self.delete(offset, length)
        self.insert(offset, text)

    def substring(self, offset: int, length: int) -> str:
        if length < 0:
            raise Invalid("substring length is negative")
        if not 0 <= offset <= len(self) - length:
            raise Invalid(f"substring range {offset}..{offset + length} out of bounds")
        return self.text()[offset : offset + length]
