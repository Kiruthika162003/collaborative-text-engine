"""Clipboard: cut, copy, and paste, each honest about what it moves.

Cut and paste feel like moving text, but in a sequence CRDT
they are a shear and a fresh insert, and the clipboard is
honest that the pasted text is new: it carries the glyphs,
not the strand ids, so pasting produces new strands and a
comment pinned to the cut text does not silently follow the
paste, because those strands are gone and pretending
otherwise lies about identity. Copy takes a range's text
without shearing, cut takes it and shears in the same
gesture, and paste inserts the held text at the caret,
minting the operations any replica weaves to the same
result. The clipboard holds one item, the last thing cut or
copied, because a clipboard that silently accumulates is a
clipboard nobody can predict, and pasting an empty
clipboard is refused rather than inserting nothing, since a
paste that does nothing looks like a broken key. The held
text is plain glyphs so it crosses between documents in a
library cleanly, a cut from one note pasting into another
as ordinary typing, which is the whole point of a
clipboard being separate from any one document.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.author import Author
from loom.errors import Invalid


@dataclass
class Clipboard:
    held: str = ""

    def copy(
        self, author: Author, start: int, count: int
    ) -> str:
        glyphs = [
            author.weave.strand_at_visible(
                start + offset
            ).glyph
            for offset in range(count)
        ]
        self.held = "".join(glyphs)
        return f"copied {len(self.held)} glyph(s)"

    def cut(
        self, author: Author, start: int, count: int
    ) -> list:
        self.copy(author, start, count)
        return author.erase_at(start, count)

    def paste(
        self, author: Author, index: int
    ) -> list:
        if not self.held:
            raise Invalid(
                "the clipboard is empty; a paste that "
                "does nothing looks like a broken key"
            )
        return author.type_at(index, self.held)

    def has_content(self) -> bool:
        return bool(self.held)
