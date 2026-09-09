"""An analytics day: two hands collide on a base, then the reading organs read the wreck.

Alice and bob both append to a shared base before exchanging,
so their first sentences share an origin and contend, and the
day closes with the analytics organs that only a real
collaboration gives anything to say: blame naming each line's
majority hand, hotspots naming where the two collided,
keywords naming what the result is about, and the readability
arithmetic on the whole. Every operation converges, so the
numbers describe one agreed document. Run with:
python -m examples.analyticsday
"""

from __future__ import annotations

from loom.author import Author
from loom.blame import render as blame_render
from loom.hotspots import report as hotspots_report
from loom.keywords import top_terms
from loom.readability import flesch_reading_ease
from loom.transcript import Tape


def main() -> int:
    tape = Tape()
    alice = Author(site="alice")
    bob = Author(site="bob")

    base = alice.type_at(0, "The plan is simple.\n")
    for op in base:
        tape.record(op)
        bob.absorb(op)

    alice_line = alice.type_at(
        alice.weave.visible_count(), "Alice favours a careful plan."
    )
    bob_line = bob.type_at(
        bob.weave.visible_count(), "Bob favours a bold plan."
    )
    for op in alice_line:
        tape.record(op)
    for op in bob_line:
        tape.record(op)
    for op in alice_line:
        bob.absorb(op)
    for op in bob_line:
        alice.absorb(op)

    print(f"text:    {alice.text()!r}")
    print(f"agree:   {alice.text() == bob.text()}")

    print()
    print("blame:")
    print(blame_render(alice.weave))

    print()
    print(hotspots_report(alice.weave))

    print()
    print(f"keywords: {', '.join(top_terms(alice.weave, 3))}")
    print(f"ease:     {flesch_reading_ease(alice.weave)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
