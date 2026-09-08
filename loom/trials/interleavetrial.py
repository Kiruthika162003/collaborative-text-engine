"""Four hands, one blank page, zero shuffling: contiguity measured.

The ugliest failure a sequence CRDT can ship is the
shuffle, four people typing four sentences into a blank
page and reading back a ransom note of interleaved
letters, and this trial measures the loom's defense
directly. Four authors each type a twelve-glyph sentence
at position zero with no deliveries until all have
finished, the cruelest concurrency for interleaving, then
everything crosses through gremlin links. The measured
verdict: the byline folds to exactly four runs, one per
hand, fragmentation one point zero, meaning not a single
letter left its sentence, and the sentences stand in
descending site order because every first glyph carries
rank one and the site name breaks the tie, dana then cara
then bob then alice, arbitrary and identically arbitrary
everywhere, which is the only kind of arbitrary allowed.
"""

from __future__ import annotations

from loom.attribution import byline
from loom.circle import Circle
from loom.trials.verdict import Verdict

SENTENCES = {
    "alice": "alpha writes ",
    "bob": "bravo drafts ",
    "cara": "cadet scribes",
    "dana": "delta pencils",
}


def run() -> Verdict:
    circle = Circle.of(
        sorted(SENTENCES),
        temperament="gremlin",
        seed=29,
    )
    minted = {
        site: circle.author(site).type_at(
            0, sentence
        )
        for site, sentence in SENTENCES.items()
    }
    for site, ops in minted.items():
        circle.say(site, ops)
    circle.settle()
    text = circle.converged()

    runs = byline(circle.author("alice").weave)
    run_sites = [site for _text, site in runs]
    fragmentation = len(runs) / len(SENTENCES)
    numbers = {
        "hands": len(SENTENCES),
        "voice_runs": len(runs),
        "fragmentation": fragmentation,
        "order": tuple(run_sites),
        "text": text,
        "every_sentence_intact": all(
            SENTENCES[site] in text
            for site in SENTENCES
        ),
    }
    holds = (
        numbers["voice_runs"] == 4
        and numbers["fragmentation"] == 1.0
        and numbers["every_sentence_intact"]
        and numbers["order"]
        == ("dana", "cara", "bob", "alice")
        and numbers["text"]
        == (
            "delta pencilscadet scribesbravo "
            "drafts alpha writes "
        )
    )
    return Verdict(
        trial="interleave",
        claim=(
            "four sentences typed onto one blank "
            "page cross gremlin mail and fold to "
            "exactly four voice runs, fragmentation "
            "one point zero, not a single letter "
            "leaving its sentence, the order settled "
            "by site name at rank one, identically "
            "arbitrary everywhere"
        ),
        numbers=numbers,
        holds=holds,
    )
