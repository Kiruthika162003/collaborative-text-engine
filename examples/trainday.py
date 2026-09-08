"""A train day: offline through the tunnels, one shake at the platform.

Alice boards with the draft, checkpoints it at the doors,
and edits through the tunnels while Bob edits at the
office. The platform reunion is one handshake, the
redline against the boarding checkpoint shows every
change wearing its hand, and the tape at each end
testifies that replay matches the living fabric. Run
with: python -m examples.trainday
"""

from __future__ import annotations

from loom.checkpoints import Shelf
from loom.handshake import shake
from loom.redlines import render
from loom.snapshot import same_fabric
from loom.station import Station
from loom.transcript import Tape


def main() -> int:
    alice = Station.named("alice")
    bob = Station.named("bob")
    alice.author.tape = Tape()
    bob.author.tape = Tape()

    for op in alice.type_at(
        0, "meeting notes: ship it"
    ):
        bob.hear(op)
    shelf = Shelf()
    shelf.keep("boarding", alice.author.weave)
    print("board:   checkpoint kept at the doors")

    alice.type_at(15, "do not ")
    bob.erase_at(0, 9)
    bob.type_at(0, "DECISION")
    print("tunnel:  both hands edit, no wire")

    print(f"shake:   {shake(alice, bob)}")
    print(f"text:    {alice.text()!r}")
    print(
        "fabric:  "
        + (
            "one digest"
            if same_fabric(
                alice.author.weave, bob.author.weave
            )
            else "DIVERGED"
        )
    )

    print()
    print("redline against boarding:")
    print(
        render(
            alice.author.weave,
            shelf.recall("boarding"),
        )
    )
    print()
    alice_testifies = alice.author.tape.testifies_for(
        alice.author.weave
    )
    bob_testifies = bob.author.tape.testifies_for(
        bob.author.weave
    )
    print(
        f"tapes:   alice replay matches: "
        f"{alice_testifies}; bob replay matches: "
        f"{bob_testifies}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
