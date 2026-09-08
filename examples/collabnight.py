"""A collaboration night: invite, edit, suggest, comment, checkpoint, review.

The fullest evening the loom hosts. A desk invites two
writers into a closed session; they redeem and draft
together through a gremlin circle; one dresses a phrase and
the other comments on it; a suggestion is proposed and
accepted; the draft is checkpointed; and the night closes
with a redline against the checkpoint and a word count. Run
with: python -m examples.collabnight
"""

from __future__ import annotations

from loom.checkpoints import Shelf
from loom.circle import Circle
from loom.comments import Comment, Margin
from loom.doors import Doorkeeper
from loom.ids import OpId
from loom.invitations import InvitationDesk
from loom.marks import Mark, Wardrobe
from loom.prose import word_count
from loom.redlines import render as redline


def main() -> int:
    door = Doorkeeper(policy="closed")
    desk = InvitationDesk(session="night", door=door)
    alice_ticket = desk.invite("alice")
    bob_ticket = desk.invite("bob")
    print(f"invite:  {desk.guest_list().splitlines()[0]}")
    desk.redeem(alice_ticket)
    print(f"redeem:  {desk.redeem(bob_ticket)}")

    circle = Circle.of(
        ["alice", "bob"],
        temperament="gremlin",
        seed=88,
    )
    circle.say(
        "alice",
        circle.author("alice").type_at(
            0, "the rough draft "
        ),
    )
    circle.settle()

    shelf = Shelf()
    shelf.keep("first-draft", circle.author("bob").weave)
    print("keep:    first-draft checkpointed")

    circle.say(
        "bob",
        circle.author("bob").type_at(16, "needs work"),
    )
    circle.settle()
    print(f"text:    {circle.converged()!r}")

    wardrobe = Wardrobe(
        weave=circle.author("alice").weave
    )
    ops = [
        circle.author("alice").weave.strand_at_visible(i)
        for i in range(4, 9)
    ]
    wardrobe.dress(
        Mark(
            id=OpId(site="alice", counter=900),
            style="bold",
            start=ops[0].id,
            end=ops[-1].id,
        )
    )
    print("dress:   'rough' wears bold")

    margin = Margin(weave=circle.author("alice").weave)
    margin.add(
        Comment(
            id=OpId(site="bob", counter=900),
            author="bob",
            body="too harsh?",
            first=ops[0].id,
            last=ops[-1].id,
        )
    )
    print(
        "comment: "
        + margin.render().splitlines()[0]
    )

    print()
    print("redline against first-draft:")
    print(
        redline(
            circle.author("alice").weave,
            shelf.recall("first-draft"),
        )
    )
    print()
    print(
        f"words:   "
        f"{word_count(circle.author('alice').weave)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
