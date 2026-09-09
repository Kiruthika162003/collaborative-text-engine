"""The hotspottrial: contention leaves fingerprints, and convergence survives all of them.

Two authors fork a shared base and storm it with fifteen
gestures each, many of them landing after the same base
strands, so their edits share origins and contend. This
measures two things at once and insists on both. First, that
the contention actually happened: the joined fabric carries
hotspots, origins where strands from both sites piled up, so
the trial is testing a real collision and not a tidy
interleaving that never overlapped. Second, that the
collisions changed nothing about the guarantee: the two
confluences, alice into bob and bob into alice, produce one
fabric digest, so every hotspot the weave recorded was also a
hotspot the weave resolved to the same order on both roads.
The guess this refutes is the intuitive one, that more
contention means more risk of divergence, that a document two
people fight over is a document that might tear. It does not.
The hotspots are the record of the fight and the single
digest is the proof the fight had one outcome, and the trial
holds exactly when both are true, because a run with no
hotspots would prove convergence of edits that never met and
a run with two digests would prove nothing worth keeping.
"""

from __future__ import annotations

import random

from loom.author import Author
from loom.confluence import confluence
from loom.fuzz import gust
from loom.hotspots import hotspots, sites_in_contention
from loom.mailroom import Mailroom
from loom.snapshot import fabric_digest
from loom.transcript import Tape
from loom.trials.verdict import Verdict


def run() -> Verdict:
    alice = Author(site="alice", tape=Tape())
    base = alice.type_at(0, "the shared base ")

    bob = Author(site="bob", tape=Tape())
    bob_room = Mailroom(author=bob)
    for op in base:
        bob_room.receive(op)

    dice_a = random.Random(41)
    dice_b = random.Random(42)
    for _ in range(15):
        gust(alice, dice_a)
        gust(bob, dice_b)

    join_ab = confluence(alice.tape, bob.tape)
    join_ba = confluence(bob.tape, alice.tape)
    spots = hotspots(join_ab)
    digests = {fabric_digest(join_ab), fabric_digest(join_ba)}

    numbers = {
        "hotspots": len(spots),
        "one_digest": len(digests) == 1,
        "sites_in_contention": sorted(sites_in_contention(join_ab)),
        "joined_length": len(join_ab.text()),
    }
    holds = numbers["hotspots"] > 0 and numbers["one_digest"]
    return Verdict(
        trial="hotspottrial",
        claim=(
            "a base two authors storm at once carries hotspots "
            "where their edits shared origins, and the two "
            "confluences still reconcile to one fabric digest, "
            "so more contention is more collaboration recorded, "
            "not more risk of divergence; the hotspots are the "
            "fight and the single digest is its one outcome"
        ),
        numbers=numbers,
        holds=holds,
    )
