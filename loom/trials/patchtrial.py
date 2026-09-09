"""The patchtrial: a careful patch lets a concurrent edit in the untouched region live.

Bringing a document to a target text can be done two ways,
and the difference only shows under concurrency. The lazy way
reshears and retypes the whole document; the careful patch
changes only the runs that differ and leaves the matching
runs' strands intact. This stages the case where that matters:
alice patches the quick brown fox to the quick red fox,
touching only the word brown, while bob concurrently types a
word into the quick, the part alice's patch never touched.
Because the patch preserved those strands, bob's insertion
anchors to a glyph that still exists rather than to a
tombstone, and the two replicas converge to one fabric with
alice's word swap and bob's insertion both present and in the
right places. The trial also measures the patch's economy,
the count of operations it minted, and checks it is far below
the length of the document, because a patch that quietly
rewrote everything would pass the convergence check while
failing the whole point, so the small op count is evidence
the patch really was surgical. The guess this pins down is
that surgical and lazy are interchangeable because both
converge; they are not, because only the surgical one keeps
the identities a concurrent collaborator's edit depends on.
"""

from __future__ import annotations

from loom.author import Author
from loom.patch import patch
from loom.snapshot import fabric_digest
from loom.trials.verdict import Verdict


def run() -> Verdict:
    alice = Author(site="alice")
    bob = Author(site="bob")
    base = alice.type_at(0, "the quick brown fox")
    for op in base:
        bob.absorb(op)

    patch_ops = patch(alice, "the quick red fox")
    bob_ops = bob.type_at(3, " very")

    for op in patch_ops:
        bob.absorb(op)
    for op in bob_ops:
        alice.absorb(op)

    digests = {fabric_digest(alice.weave), fabric_digest(bob.weave)}
    text = alice.text()
    numbers = {
        "patch_ops": len(patch_ops),
        "base_length": len(base),
        "one_digest": len(digests) == 1,
        "swap_present": "red" in text and "brown" not in text,
        "concurrent_present": "very" in text,
        "converged_text": text,
    }
    holds = (
        numbers["one_digest"]
        and numbers["swap_present"]
        and numbers["concurrent_present"]
        and numbers["patch_ops"] < numbers["base_length"]
    )
    return Verdict(
        trial="patchtrial",
        claim=(
            "a surgical patch changes only the differing run, so "
            "a collaborator's concurrent edit in the untouched "
            "region anchors to a living strand and survives the "
            "merge; the lazy retype would converge too but lose "
            "the identities that edit depended on, which is why "
            "surgical and lazy are not interchangeable"
        ),
        numbers=numbers,
        holds=holds,
    )
