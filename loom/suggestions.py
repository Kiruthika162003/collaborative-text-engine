"""Suggestions: edits that wait for a yes, held apart from the accepted cloth.

Some collaborators may propose but not impose, and
suggestion mode is that boundary drawn in operations
rather than permissions: a suggested insert is woven into
the fabric like any strand but tagged as provisional, so
the accepted text, the cloth as it reads without pending
suggestions, and the suggested text, the cloth as it would
read if every pending suggestion were accepted, are both
computable from one weave. Accepting a suggestion clears
its provisional tag, promoting the strand into the
accepted cloth with no new operation and no re-anchoring,
because the strand was always in the right place, only
wearing a maybe. Rejecting shears it, the honest deletion
of a proposal never taken. A suggested deletion is a
provisional shear, hiding the glyph from the suggested
view while leaving it in the accepted one until the
suggestion is accepted, so the reviewer sees both the
sentence as it stands and the sentence as it is asked to
become, which is the only view from which a yes or no
means anything.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Missing
from loom.ids import OpId
from loom.weave import Weave


@dataclass
class SuggestionDesk:
    weave: Weave
    provisional_inserts: set = field(
        default_factory=set
    )
    provisional_shears: dict = field(
        default_factory=dict
    )
    decided: set = field(default_factory=set)

    def suggest_insert(self, strand_id: OpId) -> str:
        if strand_id not in self.weave.by_id:
            raise Missing(
                f"{strand_id.wire()} is not in the "
                "fabric to suggest"
            )
        self.provisional_inserts.add(strand_id)
        return (
            f"{strand_id.wire()} suggested; woven but "
            "wearing a maybe"
        )

    def suggest_deletion(
        self, suggestion_id: OpId, target: OpId
    ) -> str:
        if target not in self.weave.by_id:
            raise Missing(
                f"{target.wire()} is not in the fabric"
            )
        self.provisional_shears[suggestion_id] = target
        return (
            f"{target.wire()} suggested for deletion; "
            "hidden from the ask, kept in the stands"
        )

    def accept(self, suggestion_id: OpId) -> str:
        if suggestion_id in self.provisional_inserts:
            self.provisional_inserts.discard(
                suggestion_id
            )
            self.decided.add(suggestion_id)
            return (
                f"{suggestion_id.wire()} accepted; "
                "promoted with no new operation"
            )
        if suggestion_id in self.provisional_shears:
            target = self.provisional_shears.pop(
                suggestion_id
            )
            position = self.weave.by_id[target]
            self.weave.strands[position].sheared = True
            self.decided.add(suggestion_id)
            return (
                f"{suggestion_id.wire()} accepted; the "
                "suggested deletion becomes real"
            )
        raise Missing(
            f"{suggestion_id.wire()} is not a pending "
            "suggestion"
        )

    def reject(self, suggestion_id: OpId) -> str:
        if suggestion_id in self.provisional_inserts:
            self.provisional_inserts.discard(
                suggestion_id
            )
            position = self.weave.by_id[suggestion_id]
            self.weave.strands[position].sheared = True
            self.decided.add(suggestion_id)
            return (
                f"{suggestion_id.wire()} rejected; the "
                "proposal never taken is sheared away"
            )
        if suggestion_id in self.provisional_shears:
            self.provisional_shears.pop(suggestion_id)
            self.decided.add(suggestion_id)
            return (
                f"{suggestion_id.wire()} rejected; the "
                "glyph keeps its place"
            )
        raise Missing(
            f"{suggestion_id.wire()} is not a pending "
            "suggestion"
        )

    def accepted_text(self) -> str:
        hidden = set(self.provisional_inserts)
        return "".join(
            strand.glyph
            for strand in self.weave.strands
            if not strand.sheared
            and strand.id not in hidden
        )

    def suggested_text(self) -> str:
        hidden = set(
            self.provisional_shears.values()
        )
        return "".join(
            strand.glyph
            for strand in self.weave.strands
            if not strand.sheared
            and strand.id not in hidden
        )

    def pending_count(self) -> int:
        return len(self.provisional_inserts) + len(
            self.provisional_shears
        )

    def review_page(self) -> str:
        if self.pending_count() == 0:
            return (
                "no pending suggestions; the two "
                "views agree"
            )
        return (
            f"{self.pending_count()} pending; "
            f"accepted reads {self.accepted_text()!r}, "
            f"suggested reads "
            f"{self.suggested_text()!r}"
        )
