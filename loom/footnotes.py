"""Footnotes: notes anchored in the text, numbered by where they land now.

A footnote belongs to a point in the text, and the point
moves as the document grows, so each note pins to the
strand it follows and its number is computed from reading
order rather than stored, because hand-numbered footnotes
suffer the list's exact disease: insert a note earlier and
every later number is wrong until someone fixes them all by
hand. The apparatus renders the marks in the text in
reading order, one two three by position, and the notes
below in the same order, so the number a reader sees beside
a word matches the number beside its note without either
being typed. A note whose anchor is sheared is orphaned,
kept in a separate list rather than renumbered into the
living sequence, because a note about deleted text is not
gone but it is not in the flow either, and silently
dropping it loses a remark while silently keeping it
misnumbers the rest. The count of live and orphaned notes
is reported, the two numbers an editor checks before
calling the apparatus done.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid, Missing
from loom.ids import OpId
from loom.weave import Weave


@dataclass(frozen=True)
class Note:
    id: OpId
    anchor: OpId
    body: str

    def __post_init__(self) -> None:
        if not self.body.strip():
            raise Invalid(
                "an empty footnote is a number "
                "pointing at silence"
            )


@dataclass
class Apparatus:
    weave: Weave
    notes: dict[OpId, Note] = field(
        default_factory=dict
    )

    def add(self, note: Note) -> str:
        if note.anchor not in self.weave.by_id:
            raise Missing(
                f"{note.anchor.wire()} is not in the "
                "text; a footnote needs a point to "
                "follow. Buffer it"
            )
        self.notes[note.id] = note
        return f"footnote added on {note.anchor.wire()}"

    def _live(self) -> list[Note]:
        live = []
        for note in self.notes.values():
            pos = self.weave.by_id.get(note.anchor)
            if (
                pos is not None
                and not self.weave.strands[pos].sheared
            ):
                live.append(note)
        return sorted(
            live,
            key=lambda note: self.weave.by_id[
                note.anchor
            ],
        )

    def orphaned(self) -> list[Note]:
        return [
            note
            for note in self.notes.values()
            if note not in self._live()
        ]

    def numbering(self) -> dict[OpId, int]:
        return {
            note.id: number
            for number, note in enumerate(
                self._live(), start=1
            )
        }

    def apparatus(self) -> str:
        live = self._live()
        if not live and not self.orphaned():
            return "no footnotes"
        lines = []
        for number, note in enumerate(live, start=1):
            lines.append(f"[{number}] {note.body}")
        orphans = self.orphaned()
        for note in orphans:
            lines.append(
                f"[orphaned] {note.body}"
            )
        return "\n".join(lines)

    def census(self) -> str:
        return (
            f"{len(self._live())} live footnote(s), "
            f"{len(self.orphaned())} orphaned by "
            "deletion"
        )
