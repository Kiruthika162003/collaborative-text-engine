"""A pair-writing day: two stations, one cut wire, one honest reunion.

Alice and Bob draft together, lose the wire, keep working,
and shake hands when it returns. The text converges through
the tombstones, the title race gets its quiet winner, the
status disagreement stays visible on the cover, and the tag
one hand removed survives because the other re-added it
with a dot the plucker never saw. Run with:
python -m examples.pairday
"""

from __future__ import annotations

from loom.attribution import shares
from loom.binder import Binder
from loom.handshake import shake
from loom.ids import OpId
from loom.orset import Pluck, Sprig
from loom.registers import Write
from loom.snapshot import same_fabric
from loom.station import Station


def main() -> int:
    alice = Station.named("alice")
    bob = Station.named("bob")
    for op in alice.type_at(0, "The plan: "):
        bob.hear(op)

    alice.type_at(10, "ship tuesday")
    bob.type_at(10, "test first, ")
    print("wire:    cut; both hands keep writing")

    print(f"shake:   {shake(alice, bob)}")
    print(f"text:    {alice.text()!r}")
    print(
        "fabric:  "
        + (
            "one digest at both stations"
            if same_fabric(
                alice.author.weave, bob.author.weave
            )
            else "DIVERGED"
        )
    )

    binder = Binder()
    binder.retitle(
        Write(site="alice", rank=3, value="Plan A")
    )
    print(
        "title:   "
        + binder.retitle(
            Write(site="bob", rank=5, value="The Plan")
        )
    )
    binder.declare(
        Write(site="alice", rank=7, value="final")
    )
    print(
        "status:  "
        + binder.declare(
            Write(site="bob", rank=7, value="needs-work")
        )
    )

    binder.tag(
        Sprig(
            dot=OpId(site="alice", counter=90),
            item="urgent",
        )
    )
    observed = binder.tags.dots_of("urgent")
    binder.tag(
        Sprig(
            dot=OpId(site="bob", counter=90),
            item="urgent",
        )
    )
    print(
        "untag:   "
        + binder.untag(
            Pluck(
                id=OpId(site="alice", counter=91),
                dots=observed,
            )
        )
    )

    print()
    print(binder.cover_page())
    held = shares(alice.author.weave)
    print(
        f"shares:  alice {held['alice']}%, "
        f"bob {held['bob']}%"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
