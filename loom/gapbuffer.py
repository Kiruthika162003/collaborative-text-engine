"""Gap buffer: one array with an empty gap parked at the cursor, so typing there is free.

A gap buffer holds the whole document in a single array but
leaves a stretch of unused slots, the gap, sitting at the cursor.
The characters before the cursor live at the front of the array,
the characters after it live at the back, and the gap is the
empty middle between them, so the document read out is the front
run followed by the back run with the gap skipped. Typing a
character drops it into the near end of the gap and shrinks the
gap by one, which is why editing at the cursor is cheap: nothing
moves, a slot that was empty simply becomes full. Backspace does
the reverse, widening the gap by one at its near end, and delete
widens it at its far end, so both are equally free while the
cursor stays put. The cost is entirely in moving the cursor.
Moving it means moving the gap, and moving the gap means copying
every character the gap passes over from one side to the other,
one slot at a time, so a step of the cursor is one copy and a
jump of the cursor across the document is a copy of everything
between where it was and where it goes. I had guessed moving the
cursor would be as cheap as changing an index the way it is in a
plain string; it is not, and that is the whole shape of the
structure: a gap buffer is fast exactly when edits cluster in one
region, because the gap is already there and stays there, and it
is slow exactly when the cursor leaps around a large document,
because each leap drags the gap the whole way. When the gap runs
out, because more was typed than it had room for, the array grows
by splicing in a fresh run of empty slots at the gap, which is
the one moment a lot of characters shift at once; growing it
generously makes that rare, at the cost of the empty slots the
document carries between edits. It is the mirror image of the
piece table: the piece table never moves a character and pays by
scattering the text across buffers, while the gap buffer keeps
the text contiguous and pays by moving characters whenever the
cursor travels.
"""

from __future__ import annotations

from loom.errors import Invalid

HOLE = ""


class GapBuffer:
    def __init__(self, text: str = "", gap: int = 16) -> None:
        self._chars: list[str] = list(text)
        self._gap_start = len(self._chars)
        self._chars.extend([HOLE] * max(gap, 1))
        self._gap_end = len(self._chars)

    def __len__(self) -> int:
        return len(self._chars) - (self._gap_end - self._gap_start)

    @property
    def cursor(self) -> int:
        return self._gap_start

    def text(self) -> str:
        return "".join(self._chars[: self._gap_start]) + "".join(self._chars[self._gap_end :])

    def seek(self, position: int) -> None:
        if not 0 <= position <= len(self):
            raise Invalid(f"seek position {position} out of range")
        # Moving the gap left drags each passed character to the gap's
        # far end; moving it right pulls each one to the near end.
        while self._gap_start > position:
            self._gap_start -= 1
            self._gap_end -= 1
            self._chars[self._gap_end] = self._chars[self._gap_start]
            self._chars[self._gap_start] = HOLE
        while self._gap_start < position:
            self._chars[self._gap_start] = self._chars[self._gap_end]
            self._chars[self._gap_end] = HOLE
            self._gap_start += 1
            self._gap_end += 1

    def _grow(self, needed: int) -> None:
        extra = max(needed, len(self._chars))
        self._chars[self._gap_end : self._gap_end] = [HOLE] * extra
        self._gap_end += extra

    def insert(self, text: str) -> None:
        if text == "":
            return
        if self._gap_end - self._gap_start < len(text):
            self._grow(len(text))
        for char in text:
            self._chars[self._gap_start] = char
            self._gap_start += 1

    def backspace(self, count: int = 1) -> int:
        if count < 0:
            raise Invalid("backspace count is negative")
        count = min(count, self._gap_start)
        for index in range(self._gap_start - count, self._gap_start):
            self._chars[index] = HOLE
        self._gap_start -= count
        return count

    def delete(self, count: int = 1) -> int:
        if count < 0:
            raise Invalid("delete count is negative")
        count = min(count, len(self._chars) - self._gap_end)
        for index in range(self._gap_end, self._gap_end + count):
            self._chars[index] = HOLE
        self._gap_end += count
        return count
