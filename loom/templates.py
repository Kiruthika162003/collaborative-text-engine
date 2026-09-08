"""Templates: snippets that expand into operations, so shared docs stay shared.

A snippet expansion is just typing done by a macro, and in
a collaborative document it must be exactly that: real
insert operations that every replica weaves, not a private
substitution that leaves one screen showing the expansion
and the others showing the trigger. The book holds named
snippets, expansion mints the body as ordinary typing at
the caret, and the trigger text, if the caller typed one to
invoke the snippet, is sheared in the same gesture so the
document reads the body alone, the way a human would delete
what they typed to summon it. Snippets may carry named
holes, marked with braces, and expansion returns the holes'
resolved positions so a caller can walk a user through
filling them, because a template whose blanks the writer
cannot find is a form printed without lines. A snippet
whose name is unknown is refused with the roster rather
than expanded to nothing, since an empty expansion looks
like a working feature that quietly does nothing, the worst
kind of bug because it never complains.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from loom.author import Author
from loom.errors import Invalid, Missing

HOLE = re.compile(r"\{([a-z_]+)\}")


@dataclass
class TemplateBook:
    snippets: dict = field(default_factory=dict)

    def define(self, name: str, body: str) -> str:
        if not name.strip():
            raise Invalid(
                "a nameless snippet cannot be summoned"
            )
        if not body:
            raise Invalid(
                f"{name} expands to nothing; an empty "
                "snippet is a feature that quietly "
                "does nothing"
            )
        self.snippets[name] = body
        return f"{name} defined, {len(body)} char(s)"

    def holes(self, name: str) -> list[str]:
        body = self.snippets.get(name)
        if body is None:
            raise Missing(f"{name} is not a snippet")
        return HOLE.findall(body)

    def expand_at(
        self,
        author: Author,
        name: str,
        index: int,
        trigger_len: int = 0,
    ) -> list:
        body = self.snippets.get(name)
        if body is None:
            raise Missing(
                f"{name} is not a snippet; the book "
                "holds "
                + (
                    ", ".join(sorted(self.snippets))
                    or "nothing"
                )
            )
        if trigger_len:
            author.erase_at(
                index - trigger_len, trigger_len
            )
            index -= trigger_len
        return author.type_at(index, body)

    def roster(self) -> str:
        if not self.snippets:
            return "an empty book; no snippets defined"
        lines = [
            f"{len(self.snippets)} snippet(s):"
        ]
        for name in sorted(self.snippets):
            holes = self.holes(name)
            note = (
                f" ({len(holes)} hole(s))"
                if holes
                else ""
            )
            lines.append(f"  {name}{note}")
        return "\n".join(lines)
