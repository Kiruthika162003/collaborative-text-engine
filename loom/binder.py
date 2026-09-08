"""The binder: the document around the text, each field wearing the right CRDT.

A document is text plus decisions about the text, and the
binder assigns each decision the register its stakes
deserve. The title takes the last-writer register because
a title race deserves a quiet winner, two hands renaming
at once being a shrug, not a crisis. The status takes the
every-voice register because doneness is exactly where
disagreement must stay visible, one hand marking final
while another marks needs-work being a conversation the
document should force, not settle by coin flip. The tags
ride the basket so removing urgent never eats the urgent
someone else was re-adding, and the cover page prints all
three with their disagreements showing, since a cover
that tidies the argument away is the binder taking sides.
The binder never touches the weave; text is the loom's
business, and the two meet only on the page.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid
from loom.orset import Basket, Pluck, Sprig
from loom.registers import EveryVoice, LastWriter, Write


@dataclass
class Binder:
    title: LastWriter = field(
        default_factory=LastWriter
    )
    status: EveryVoice = field(
        default_factory=EveryVoice
    )
    tags: Basket = field(default_factory=Basket)

    def retitle(self, entry: Write) -> str:
        return self.title.write(entry)

    def declare(self, entry: Write) -> str:
        return self.status.write(entry)

    def tag(self, sprig: Sprig) -> str:
        return self.tags.add(sprig)

    def untag(self, pluck: Pluck) -> str:
        return self.tags.pluck(pluck)

    def cover_page(self) -> str:
        try:
            shown_title = self.title.read()
        except Invalid:
            shown_title = "(untitled)"
        lines = [f"title: {shown_title}"]
        lines.append(f"status: {self.status.page()}")
        held = self.tags.items()
        if held:
            lines.append(
                "tags: " + ", ".join(held)
            )
        else:
            lines.append("tags: none")
        lines.append(
            "disagreements shown as found; a cover "
            "that tidies the argument away is the "
            "binder taking sides"
        )
        return "\n".join(lines)
