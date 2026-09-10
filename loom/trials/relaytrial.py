"""The relaytrial: delivered backward, a run still converges once its first glyph uncorks it.

A network can hand a replica the operations of an edit in any
order, and causal readiness is what keeps that from mattering. This
stages the hardest order: alice types a run of glyphs, minting them
left to right so each originates on the one before it, and bob
receives them through his mailroom in fully reversed order, the last
glyph first and the first glyph last. Every early arrival names an
origin bob has not woven yet, so the mailroom shelves it rather than
guessing, and the shelf grows with each arrival until it holds all
but one; then the very first glyph arrives last, the one glyph that
originates on the start of the document and so is ready at once, and
weaving it uncorks the shelf, each swept glyph making the next ready
until the run drains in order. I had guessed reversed delivery would
either error, since most arrivals reference a missing origin, or
need the whole run buffered and sorted before anything could weave;
the mailroom neither errors nor sorts, it shelves each unready
arrival with its reason and lets one ready arrival cascade through
the rest, so the peak shelf depth is exactly one less than the run
and the final fabric is identical to what in-order delivery builds.
That is the property pinned down: causal readiness makes delivery
order irrelevant to the converged result, buffering exactly the
arrivals that are not yet safe and no more, so a replica fed an edit
backward ends where a replica fed it forward ends, which is what
lets the network be as careless about order as the echotrial showed
it can be about repeats.
"""

from __future__ import annotations

from loom.author import Author
from loom.mailroom import Mailroom
from loom.snapshot import fabric_digest
from loom.trials.verdict import Verdict


def run() -> Verdict:
    alice = Author(site="alice")
    typed = alice.type_at(0, "the brown fox")

    bob = Mailroom(author=Author(site="bob"))
    peak_shelf = 0
    for op in reversed(typed):
        bob.receive(op)
        peak_shelf = max(peak_shelf, len(bob.shelf))

    digests = {fabric_digest(alice.weave), fabric_digest(bob.author.weave)}
    numbers = {
        "run_length": len(typed),
        "peak_shelf": peak_shelf,
        "woven": bob.woven,
        "still_waiting": len(bob.shelf),
        "one_digest": len(digests) == 1,
        "converged_text": bob.author.text(),
    }
    holds = (
        numbers["one_digest"]
        and numbers["still_waiting"] == 0
        and numbers["woven"] == numbers["run_length"]
        and numbers["peak_shelf"] == numbers["run_length"] - 1
        and numbers["converged_text"] == "the brown fox"
    )
    return Verdict(
        trial="relaytrial",
        claim=(
            "delivered in fully reversed order, a typed run shelves "
            "every arrival but the first, whose weaving uncorks the "
            "shelf and cascades the rest into place, so the peak "
            "shelf is one less than the run and the fabric matches "
            "in-order delivery; causal readiness makes delivery "
            "order irrelevant to the converged result"
        ),
        numbers=numbers,
        holds=holds,
    )
