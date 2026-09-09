"""The casetrial: uppercasing a word does not eat a letter typed into it at once.

A case transform is a run of shears and inserts, and the
worry is what happens when someone types into the middle of
the word while it is being uppercased somewhere else. This
stages exactly that: alice uppercases hello to HELLO,
shearing five lowercase letters and weaving five capitals,
while bob concurrently types a stray glyph between the two
els, and then the two replicas exchange operations. The
guess worth testing was that one gesture might swallow the
other, the shear of the old letter taking bob's insert with
it or bob's insert stranding the transform. It does neither.
The transform shears letters it named by id, bob's insert
anchors to a strand that still exists as a tombstone even
after it is sheared, and the two replicas converge to one
fabric digest with the capitals standing and bob's glyph
surviving in its place, lowercase because it was never part
of the word alice transformed. The measured facts are the
five shears alice minted, the single digest across both
replicas, and bob's glyph present in the converged text,
because a case transform that quietly dropped a collaborator's
keystroke would be a data-loss bug wearing the costume of a
formatting command.
"""

from __future__ import annotations

from loom.author import Author
from loom.casing import upper
from loom.snapshot import fabric_digest
from loom.trials.verdict import Verdict
from loom.weave import Shear

MARK = "X"


def run() -> Verdict:
    alice = Author(site="alice")
    bob = Author(site="bob")
    base = alice.type_at(0, "hello world")
    for op in base:
        bob.absorb(op)

    alice_ops = upper(alice, 0, 5).ops
    bob_ops = bob.type_at(3, MARK)

    for op in alice_ops:
        bob.absorb(op)
    for op in bob_ops:
        alice.absorb(op)

    shears = sum(1 for op in alice_ops if isinstance(op, Shear))
    digests = {fabric_digest(alice.weave), fabric_digest(bob.weave)}
    numbers = {
        "shears_by_alice": shears,
        "one_digest": len(digests) == 1,
        "mark_survived": MARK in alice.text() and MARK in bob.text(),
        "texts_equal": alice.text() == bob.text(),
        "converged_text": alice.text(),
    }
    holds = (
        numbers["one_digest"]
        and numbers["mark_survived"]
        and numbers["texts_equal"]
        and numbers["shears_by_alice"] == 5
    )
    return Verdict(
        trial="casetrial",
        claim=(
            "uppercasing a word while a collaborator types into "
            "it converges to one fabric with the capitals "
            "standing and the typed glyph surviving, because the "
            "shears name letters by id and the concurrent insert "
            "anchors to a strand that lives on as a tombstone; a "
            "transform that dropped the keystroke would be data "
            "loss dressed as a formatting command"
        ),
        numbers=numbers,
        holds=holds,
    )
