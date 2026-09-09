"""Glossary: defined terms and where each one first appears in the text.

A glossary is a set of terms with definitions, and its
useful trick over a plain dictionary is finding where each
term first appears in a document, so a reader can link the
first use to its definition and leave the rest alone, which
is how a well-edited reference reads. The search is word
boundaried and case insensitive, because Term and term are
the same word to a reader and a match inside a longer word
is not a use of the term at all, and multi-word terms like
version vector are matched whole. Each first use pins to the
strand where the term starts, so the link survives edits
above it, and a term that never appears is simply absent
from the results rather than reported as a broken link. The
one limit is named rather than hidden: the match does not
know inflections, so a glossary term cat is not found in the
word cats, and a reader who needs plurals linked must define
them, because guessing that cats means cat is the kind of
helpfulness that also links class to a glossary entry for
clas. Definitions are looked up case insensitively too, so
the term as written in the prose finds its entry however the
author capitalised it when defining it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from loom.errors import Invalid
from loom.ids import OpId
from loom.weave import Weave


@dataclass(frozen=True)
class FirstUse:
    term: str
    pin: OpId
    position: int


@dataclass
class Glossary:
    entries: dict[str, str] = field(default_factory=dict)

    def define(self, term: str, definition: str) -> str:
        key = term.strip().lower()
        if not key:
            raise Invalid("a glossary term cannot be blank")
        if not definition.strip():
            raise Invalid(
                f"the term {term!r} needs a definition, not an "
                "empty promise"
            )
        self.entries[key] = definition.strip()
        return f"defined {key!r}"

    def lookup(self, term: str) -> str | None:
        return self.entries.get(term.strip().lower())

    def _visible_ids(self, weave: Weave) -> list[OpId]:
        return [
            strand.id for strand in weave.strands if not strand.sheared
        ]

    def first_uses(self, weave: Weave) -> list[FirstUse]:
        text = weave.text()
        ids = self._visible_ids(weave)
        found = []
        for term in self.entries:
            pattern = re.compile(
                r"\b" + re.escape(term) + r"\b", re.IGNORECASE
            )
            match = pattern.search(text)
            if match is not None:
                found.append(
                    FirstUse(
                        term=term,
                        pin=ids[match.start()],
                        position=match.start(),
                    )
                )
        return sorted(found, key=lambda use: use.position)

    def unused(self, weave: Weave) -> list[str]:
        used = {use.term for use in self.first_uses(weave)}
        return sorted(term for term in self.entries if term not in used)

    def report(self, weave: Weave) -> str:
        uses = self.first_uses(weave)
        if not self.entries:
            return "an empty glossary defines nothing"
        lines = [f"{len(self.entries)} term(s), {len(uses)} used:"]
        for use in uses:
            lines.append(f"  {use.term} first at position {use.position}")
        idle = self.unused(weave)
        if idle:
            lines.append("  unused: " + ", ".join(idle))
        return "\n".join(lines)
