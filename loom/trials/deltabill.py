"""The delta bill: what sync costs when memory does the arithmetic.

A hundred glyphs are typed and shared, then one hand makes
a handful of small edits while the wire is down, and the
trial prices the reunion two ways. The naive strategy
ships every journaled operation both directions, and the
first guess priced it at two hundred sixteen by imagining
both journals already reunited; the honest price is taken
before the shake, one hundred plus one hundred eight, two
hundred eight, and the guess stays corrected here because
even a bill can beg the question. The handshake ships what
the other clock lacks and nothing else: eight to alice,
zero to bob, the station that stayed still receiving
everything and sending nothing, which is the shape
reunions actually have. Two hundred eight naive against
eight shipped is a ratio of twenty-six, measured and
locked, and every later module that touches the wire
answers to this page for its appetite.
"""

from __future__ import annotations

from loom.handshake import shake
from loom.station import Station
from loom.trials.verdict import Verdict


def run() -> Verdict:
    alice = Station.named("alice")
    bob = Station.named("bob")
    for op in alice.type_at(0, "x" * 100):
        bob.hear(op)

    bob.type_at(50, "edit")
    bob.erase_at(10, 3)
    bob.type_at(0, "!")

    naive_cost = alice.journal.size() + (
        bob.journal.size()
    )
    receipt = shake(alice, bob)
    tail = receipt.split(": ", 1)[1]
    to_bob_text, to_alice_text = tail.split(", ")
    shipped = int(to_bob_text.split()[0]) + int(
        to_alice_text.split()[0]
    )

    numbers = {
        "alice_journal": alice.journal.size(),
        "bob_journal": bob.journal.size(),
        "naive_cost_both_ways": naive_cost,
        "shipped": shipped,
        "converged": alice.text() == bob.text(),
        "savings_ratio": (
            naive_cost // shipped if shipped else 0
        ),
    }
    holds = (
        numbers["converged"]
        and numbers["shipped"] == 8
        and numbers["naive_cost_both_ways"] == 208
        and numbers["savings_ratio"] == 26
        and numbers["alice_journal"] == 108
        and numbers["bob_journal"] == 108
    )
    return Verdict(
        trial="deltabill",
        claim=(
            "the handshake ships eight operations "
            "where naive full exchange would ship two "
            "hundred and eight, the still station "
            "receiving everything and sending "
            "nothing, which is the shape reunions "
            "actually have"
        ),
        numbers=numbers,
        holds=holds,
    )
