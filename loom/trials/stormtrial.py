"""Eighty gusts, three hands, a gremlin postal service: still one cloth.

The duet proved the sensible case; this trial proves the
senseless one, eighty seeded gestures from three authors
typing and erasing over each other while every link
shuffles batches and manufactures duplicates. The first
claimed equation, final length equals typed minus erased,
failed by exactly ten, and the failure was the lesson:
sixty-six shears were minted but only fifty-six strands
died, because concurrent erasures overlap and ten scissors
closed on glyphs already dead, two scissors one cut, ten
times. Erasure counts gestures; tombstones count victims;
concurrent editing is precisely the condition under which
those numbers part ways, and an engine that forced them
equal would be double-deleting. The honest equation, final
length equals typed minus victims, holds to the glyph, the
tombstone census agrees at every site, and one hundred
forty-seven manufactured duplicates changed nothing, all
measured from seed seven and then locked: if the engine
ever drifts, this page is the first to say so.
"""

from __future__ import annotations

from loom.circle import Circle
from loom.fuzz import Storm
from loom.trials.verdict import Verdict


def run() -> Verdict:
    circle = Circle.of(
        ["alice", "bob", "cara"],
        temperament="gremlin",
        seed=7,
    )
    storm = Storm(rounds=80, seed=7)
    storm.blow_through(circle)
    text = circle.converged()

    tombstones = {
        site: author.weave.tombstone_count()
        for site, author in circle.authors.items()
    }
    duplicates = sum(
        link.duplicated
        for link in circle.links.values()
    )
    victims = numbers_victims = tombstones["alice"]
    numbers = {
        "typed": storm.typed,
        "erased_gestures": storm.erased,
        "victims": numbers_victims,
        "double_cuts": storm.erased - victims,
        "final_length": len(text),
        "arithmetic_holds": (
            len(text) == storm.typed - victims
        ),
        "tombstones": tuple(
            tombstones[site]
            for site in sorted(tombstones)
        ),
        "duplicates_manufactured": duplicates,
        "mid_flight": storm.mid_flight_deliveries,
    }
    holds = (
        numbers["arithmetic_holds"]
        and len(set(numbers["tombstones"])) == 1
        and numbers["typed"] == 144
        and numbers["erased_gestures"] == 66
        and numbers["victims"] == 56
        and numbers["double_cuts"] == 10
        and numbers["final_length"] == 88
        and numbers["duplicates_manufactured"] == 147
    )
    return Verdict(
        trial="storm",
        claim=(
            "eighty seeded gusts through gremlin mail "
            "converge to one text whose length equals "
            "typed minus victims, not typed minus "
            "erasures, because ten scissors closed on "
            "glyphs already dead; gestures and victims "
            "part ways exactly when editing is "
            "concurrent, and forcing them equal would "
            "be double-deleting"
        ),
        numbers=numbers,
        holds=holds,
    )
