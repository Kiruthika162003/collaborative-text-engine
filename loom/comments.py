"""Comments: remarks anchored to a stretch of cloth, surviving the edits around them.

A comment attached to characters twelve through twenty is
pointing at the wrong words by lunchtime; here a comment
pins to the first and last strand of the stretch it
discusses, so it keeps discussing the same text even as
the paragraph around it grows and shrinks. A comment whose
stretch is edited becomes stale rather than wrong, and the
margin says so, because a comment that silently re-points
to whatever now sits at its old position is worse than no
comment, it is a lie with a timestamp. Comments thread:
replies carry their parent's id and the margin renders the
conversation in order, and resolving is add-wins like
every other shared intention, one resolver's mark closing
the thread while the text it discussed stays exactly where
it was, because resolving a comment settles the
conversation, not the cloth. A comment on a stretch that
has been entirely sheared is shown against its tombstones
with a note, the remark outliving the words being the
whole reason margins exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid, Missing
from loom.ids import OpId
from loom.weave import Weave


@dataclass(frozen=True)
class Comment:
    id: OpId
    author: str
    body: str
    first: OpId
    last: OpId
    parent: OpId | None = None

    def __post_init__(self) -> None:
        if not self.body.strip():
            raise Invalid(
                "an empty comment is a margin mark "
                "for nothing"
            )


@dataclass
class Margin:
    weave: Weave
    comments: dict[OpId, Comment] = field(
        default_factory=dict
    )
    resolved: set[OpId] = field(default_factory=set)

    def _quoted(self, comment: Comment) -> str:
        first = self.weave.by_id.get(comment.first)
        last = self.weave.by_id.get(comment.last)
        if first is None or last is None:
            return ""
        return "".join(
            strand.glyph
            for strand in self.weave.strands[
                first : last + 1
            ]
            if not strand.sheared
        )

    def add(self, comment: Comment) -> str:
        if comment.first not in self.weave.by_id:
            raise Missing(
                f"{comment.first.wire()} is not in "
                "the fabric; a pin needs a strand. "
                "Buffer it"
            )
        if (
            comment.parent is not None
            and comment.parent not in self.comments
        ):
            raise Missing(
                f"{comment.parent.wire()} is not a "
                "comment here; a reply needs a "
                "remark to answer. Buffer it"
            )
        self.comments[comment.id] = comment
        return (
            f"{comment.author} remarked on "
            f"{self._quoted(comment)!r}"
        )

    def is_stale(self, comment_id: OpId) -> bool:
        comment = self.comments[comment_id]
        first = self.weave.by_id.get(comment.first)
        last = self.weave.by_id.get(comment.last)
        if first is None or last is None:
            return True
        stretch = self.weave.strands[first : last + 1]
        return any(
            strand.sheared for strand in stretch
        )

    def resolve(
        self, comment_id: OpId, by: str
    ) -> str:
        if comment_id not in self.comments:
            raise Missing(
                f"{comment_id.wire()} is not a "
                "comment to resolve"
            )
        self.resolved.add(comment_id)
        return (
            f"{by} resolved the thread; the "
            "conversation settles, the cloth does not"
        )

    def _replies(self, parent_id: OpId) -> list[Comment]:
        return sorted(
            (
                comment
                for comment in self.comments.values()
                if comment.parent == parent_id
            ),
            key=lambda comment: (
                comment.id.counter,
                comment.id.site,
            ),
        )

    def render(self) -> str:
        roots = sorted(
            (
                comment
                for comment in self.comments.values()
                if comment.parent is None
            ),
            key=lambda comment: (
                comment.id.counter,
                comment.id.site,
            ),
        )
        if not roots:
            return "no comments in the margin"
        lines = []
        for root in roots:
            state = (
                "resolved"
                if root.id in self.resolved
                else "open"
            )
            stale = (
                " STALE"
                if self.is_stale(root.id)
                else ""
            )
            lines.append(
                f"[{state}{stale}] {root.author} on "
                f"{self._quoted(root)!r}: {root.body}"
            )
            for reply in self._replies(root.id):
                lines.append(
                    f"    {reply.author}: {reply.body}"
                )
        return "\n".join(lines)
