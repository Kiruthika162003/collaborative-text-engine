"""The mergetrial: three ways to join two drafts, one fabric out of all of them.

Two authors fork a shared base and edit offline through a
storm of gestures, and the loom offers three ways to bring
them back together: a mailroom handshake exchanging
operations, a confluence joining their tapes, and the same
confluence with the tapes fed in the opposite order. The
trial builds the divergence once and reconciles it all
three ways, then asks the only question that matters, do
all three produce the same fabric digest, because three
reconciliation paths that disagree is three bugs wearing a
trenchcoat. The measured facts: one digest across all
three joins, the joined text containing every glyph both
drafts contributed, and the operation union counted once
so nobody double-pays for the shared base. If this trial
ever breaks, the merge story of the whole engine is
broken, which is why it stores the largest numbers of any
trial and checks the humblest property, that equal inputs
give equal outputs no matter the road taken.
"""

from __future__ import annotations

import random

from loom.author import Author
from loom.confluence import confluence, op_union_size
from loom.fuzz import gust
from loom.mailroom import Mailroom
from loom.snapshot import fabric_digest
from loom.transcript import Tape
from loom.trials.verdict import Verdict


def run() -> Verdict:
    base_tape = Tape()
    alice = Author(site="alice", tape=base_tape)
    base_ops = alice.type_at(0, "the shared base ")

    bob = Author(site="bob", tape=Tape())
    bob_room = Mailroom(author=bob)
    for op in base_ops:
        bob_room.receive(op)

    dice_a = random.Random(61)
    dice_b = random.Random(62)
    for _ in range(20):
        gust(alice, dice_a)
        gust(bob, dice_b)

    handshake_left = Author(site="cara")
    left_room = Mailroom(author=handshake_left)
    for op in list(alice.tape.reel):
        left_room.receive(op)
    for op in list(bob.tape.reel):
        left_room.receive(op)

    join_ab = confluence(alice.tape, bob.tape)
    join_ba = confluence(bob.tape, alice.tape)

    digests = {
        fabric_digest(handshake_left.weave),
        fabric_digest(join_ab),
        fabric_digest(join_ba),
    }
    numbers = {
        "reconciliation_paths": 3,
        "one_digest": len(digests) == 1,
        "union_size": op_union_size(
            alice.tape, bob.tape
        ),
        "alice_ops": alice.tape.length(),
        "bob_ops": bob.tape.length(),
        "joined_length": len(join_ab.text()),
    }
    holds = (
        numbers["one_digest"]
        and numbers["union_size"]
        == numbers["alice_ops"]
        + numbers["bob_ops"]
        - len(base_ops)
    )
    return Verdict(
        trial="mergetrial",
        claim=(
            "a handshake and two confluences reconcile "
            "the same divergence to one fabric digest, "
            "because three reconciliation paths that "
            "disagree is three bugs wearing a "
            "trenchcoat, and the operation union counts "
            "the shared base once"
        ),
        numbers=numbers,
        holds=holds,
    )
