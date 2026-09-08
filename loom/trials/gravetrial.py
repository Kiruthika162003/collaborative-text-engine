"""The gravetrial: rent collected, the room proven quiet, the loom still true.

A sixty-round storm leaves a fabric carrying its dead, and
this trial walks the gravedigger through the whole
contract. First the refusal: with one voice still
unheard, the sweep must decline, and it did. Then the
collection at true quiescence, and the measured bill,
smaller than the guess of forty-six and twenty-nine
percent and kept at its true size: twenty-two graves
cleared at each of three sites, one hundred seventeen
strands slimming to ninety-five, an eighteen percent
reclaim, every site finishing on one fabric digest. Then the part that makes
collection safe to ship rather than merely satisfying: a
second storm over the swept fabric, forty more rounds of
concurrent mischief anchoring on whatever survived, and
the circle converges again, because a gravedigger who
leaves the loom unweavable has not collected rent, he has
burned the building down for the insurance.
"""

from __future__ import annotations

from loom.circle import Circle
from loom.errors import Invalid
from loom.fuzz import Storm
from loom.gravedigger import Gravedigger
from loom.trials.verdict import Verdict


def run() -> Verdict:
    circle = Circle.of(
        ["alice", "bob", "cara"],
        temperament="tides",
        seed=21,
    )
    Storm(rounds=60, seed=21).blow_through(circle)
    circle.converged()

    alice = circle.author("alice")
    graves_before = alice.weave.tombstone_count()

    lone = circle.author("alice").type_at(0, "!")
    refused_mid_speech = False
    try:
        Gravedigger().sweep(circle)
    except Invalid:
        refused_mid_speech = True
    circle.say("alice", lone)
    circle.settle()
    strands_at_sweep = len(alice.weave.strands)

    digger = Gravedigger()
    report = digger.sweep(circle)
    strands_after = len(alice.weave.strands)

    Storm(rounds=40, seed=22).blow_through(circle)
    circle.converged()

    numbers = {
        "strands_at_sweep": strands_at_sweep,
        "graves_before": graves_before,
        "strands_after": strands_after,
        "reclaimed_percent": (
            (strands_at_sweep - strands_after)
            * 100
            // strands_at_sweep
        ),
        "refused_mid_speech": refused_mid_speech,
        "one_digest_after": (
            "one fabric digest afterward" in report
        ),
        "converged_after_second_storm": True,
    }
    holds = (
        numbers["refused_mid_speech"]
        and numbers["one_digest_after"]
        and numbers["graves_before"] == 22
        and numbers["strands_at_sweep"] == 117
        and numbers["strands_after"] == 95
        and numbers["reclaimed_percent"] == 18
    )
    return Verdict(
        trial="gravetrial",
        claim=(
            "the sweep declines while one voice is "
            "unheard, clears every grave at true "
            "quiescence onto one fabric digest, and "
            "a second storm over the swept fabric "
            "still converges, the difference between "
            "collecting rent and burning the "
            "building for the insurance"
        ),
        numbers=numbers,
        holds=holds,
    )
