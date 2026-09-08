"""The longhaul: five hands, three hundred rounds, and the arithmetic intact.

Small trials prove mechanisms; the longhaul proves
stamina. Five authors gust for three hundred seeded
rounds through gremlin links, deliveries crossing
mid-storm, and at the end the trial asks only the
questions that matter at scale and locks their measured
answers: one text everywhere, twenty links manufacturing
over a thousand duplicates that changed nothing, the
honest equation holding at size, five hundred eighty
typed minus one hundred forty-seven victims reading four
hundred thirty-three on every screen, and eleven double
cuts where scissors met at the same glyph. The numbers
are large enough to be boring, which is the point: a
convergence engine earns trust not when the clever case
passes but when three hundred rounds of uncoordinated
typing produce nothing to talk about.
"""

from __future__ import annotations

from loom.circle import Circle
from loom.fuzz import Storm
from loom.snapshot import fabric_digest
from loom.trials.verdict import Verdict

SITES = ("alice", "bob", "cara", "dana", "erin")


def run() -> Verdict:
    circle = Circle.of(
        list(SITES), temperament="gremlin", seed=47
    )
    storm = Storm(rounds=300, seed=47)
    storm.blow_through(circle)
    text = circle.converged()

    victims = circle.author(
        "alice"
    ).weave.tombstone_count()
    digests = {
        fabric_digest(author.weave)
        for author in circle.authors.values()
    }
    duplicates = sum(
        link.duplicated
        for link in circle.links.values()
    )
    numbers = {
        "sites": len(SITES),
        "links": len(circle.links),
        "typed": storm.typed,
        "erase_gestures": storm.erased,
        "victims": victims,
        "double_cuts": storm.erased - victims,
        "final_length": len(text),
        "arithmetic_holds": (
            len(text) == storm.typed - victims
        ),
        "one_digest": len(digests) == 1,
        "duplicates_manufactured": duplicates,
    }
    holds = (
        numbers["one_digest"]
        and numbers["arithmetic_holds"]
        and numbers["links"] == 20
        and numbers["typed"] == 580
        and numbers["erase_gestures"] == 158
        and numbers["victims"] == 147
        and numbers["double_cuts"] == 11
        and numbers["final_length"] == 433
        and numbers["duplicates_manufactured"] == 1010
    )
    return Verdict(
        trial="longhaul",
        claim=(
            "five hands and three hundred rounds "
            "through twenty gremlin links produce "
            "one digest and an equation that holds "
            "at size, typed minus victims, eleven "
            "double cuts and a thousand and ten "
            "duplicates changing nothing; numbers "
            "large enough to be boring, which is "
            "the point"
        ),
        numbers=numbers,
        holds=holds,
    )
