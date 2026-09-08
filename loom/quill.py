"""The quill: raw keystrokes at a caret, translated into honest gestures.

Editors do not receive gestures, they receive keys, and
the quill is the layer that stands where the keyboard
meets the loom: it holds a caret position, types printable
keys at it, moves it with arrows and home and end, and
translates backspace and delete into the shears they
really are, backspace eating the glyph left of the caret
and delete the glyph under it, each refusing politely at
the edges where there is nothing to eat. Every keystroke
returns the operations it minted so the caller can put
them on whatever wire it runs, an empty list meaning the
key moved the caret and moved nothing else, and the caret
arithmetic is tested at the edges because off-by-one at a
caret is the oldest bug in text editing and the loom does
not intend to write it again. The quill holds no state
but the position; the fabric is the author's, and two
quills over one author is two cursors, not two documents.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.author import Author
from loom.errors import Invalid
from loom.weave import Op

ARROW_LEFT = "<left>"
ARROW_RIGHT = "<right>"
KEY_HOME = "<home>"
KEY_END = "<end>"
KEY_BACKSPACE = "<backspace>"
KEY_DELETE = "<delete>"

MOTIONS = (
    ARROW_LEFT,
    ARROW_RIGHT,
    KEY_HOME,
    KEY_END,
)


@dataclass
class Quill:
    author: Author
    caret: int = 0
    swallowed: int = 0

    def _length(self) -> int:
        return self.author.weave.visible_count()

    def press(self, key: str) -> list[Op]:
        if key in MOTIONS:
            if key == ARROW_LEFT:
                self.caret = max(0, self.caret - 1)
            elif key == ARROW_RIGHT:
                self.caret = min(
                    self._length(), self.caret + 1
                )
            elif key == KEY_HOME:
                self.caret = 0
            else:
                self.caret = self._length()
            return []
        if key == KEY_BACKSPACE:
            if self.caret == 0:
                self.swallowed += 1
                return []
            ops = self.author.erase_at(
                self.caret - 1, 1
            )
            self.caret -= 1
            return ops
        if key == KEY_DELETE:
            if self.caret >= self._length():
                self.swallowed += 1
                return []
            return self.author.erase_at(self.caret, 1)
        if len(key) != 1:
            raise Invalid(
                f"{key!r} is not a key this quill "
                "knows; printable glyphs and the "
                "named keys only"
            )
        ops = self.author.type_at(self.caret, key)
        self.caret += 1
        return ops

    def press_many(self, keys: list[str]) -> list[Op]:
        minted: list[Op] = []
        for key in keys:
            minted.extend(self.press(key))
        return minted

    def type_words(self, text: str) -> list[Op]:
        return self.press_many(list(text))

    def where(self) -> str:
        return (
            f"caret at {self.caret} of "
            f"{self._length()}; "
            f"{self.swallowed} keystroke(s) "
            "swallowed at the edges"
        )
