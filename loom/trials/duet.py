"""Two hands, crossed deliveries, one cloth: the trial that earned its keep.

Alice types a sentence; Bob, holding a copy, inserts brown
before fox while Alice concurrently erases quick, and each
side's operations reach the other in reverse order. The
first run of this trial refuted the engine's own design
twice, and both refutations stay recorded. The text came
back as the foxbrown, converged but absurd, because sibling
contests were being judged by delivery counters and Bob's
counter said one while his eyes had seen thirteen; the fix
is the witness rank, and the fix lives in the weave with
the failure named in its docstring. And the shelving count
came back six where five was true, because the counter
matched the word shelved inside the sweep's own receipt
about draining shelved arrivals, a measurement instrument
reading its own reflection; the count now matches the
shelving receipt exactly. With both corrections the claim
holds: the brown fox stands where quick was cut, woven
through a dead glyph that still anchors, which is the
entire argument for tombstones in five words of English.
"""

from __future__ import annotations

from loom.author import Author
from loom.mailroom import Mailroom
from loom.trials.verdict import Verdict


def run() -> Verdict:
    alice = Author(site="alice")
    bob = Author(site="bob")
    to_bob = Mailroom(author=bob)
    to_alice = Mailroom(author=alice)

    sentence = alice.type_at(0, "the quick fox")
    for op in sentence:
        to_bob.receive(op)

    bob_inserts = bob.type_at(10, "brown ")
    alice_shears = alice.erase_at(4, 6)

    shelved_at_bob = 0
    for op in reversed(alice_shears):
        if " shelved:" in to_bob.receive(op):
            shelved_at_bob += 1
    shelved_at_alice = 0
    for op in reversed(bob_inserts):
        if " shelved:" in to_alice.receive(op):
            shelved_at_alice += 1

    numbers = {
        "alice_text": alice.text(),
        "bob_text": bob.text(),
        "converged": alice.text() == bob.text(),
        "shelved_at_bob": shelved_at_bob,
        "shelved_at_alice": shelved_at_alice,
        "tombstones_each": (
            alice.weave.tombstone_count(),
            bob.weave.tombstone_count(),
        ),
        "strands_each": (
            len(alice.weave.strands),
            len(bob.weave.strands),
        ),
        "bob_first_rank": bob_inserts[0].rank,
    }
    holds = (
        numbers["converged"]
        and numbers["alice_text"] == "the brown fox"
        and numbers["shelved_at_bob"] == 5
        and numbers["shelved_at_alice"] == 5
        and numbers["tombstones_each"] == (6, 6)
        and numbers["strands_each"] == (19, 19)
        and numbers["bob_first_rank"] == 14
    )
    return Verdict(
        trial="duet",
        claim=(
            "crossed reversed deliveries converge to "
            "the sensible merge, the brown fox "
            "standing where quick was cut through a "
            "dead glyph that still anchors, with "
            "Bob's first insert ranked fourteen "
            "because he had witnessed thirteen"
        ),
        numbers=numbers,
        holds=holds,
    )
