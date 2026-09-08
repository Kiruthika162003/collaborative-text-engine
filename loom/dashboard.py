"""The dashboard: a session's activity read from a tape and a fabric at once.

Where the health glass reads a document's condition, the
dashboard reads a session's activity: who wrote, in what
rhythm, over what shape of text, drawing the tape organs
and the fabric organs into one page a facilitator scans
between turns. It borrows cadence for the rhythm and the
handoff count, attribution for who owns the surviving
words, the census for the fabric's shape, and the word
count for size, each in its own words under the standing
rule that a dashboard which paraphrases its instruments
turns four precise readings into one vague impression. The
page adds one derived number of its own, the balance, the
busiest hand's share of the surviving words, because a
facilitator's real question is whether the document is a
conversation or a monologue and that share answers it in a
single figure: a lone author holds the whole hundred and
reads as the monologue it is, where a max-minus-min gap
would have called a solo writer's zero spread a
conversation, which was the first guess and was wrong. The
dashboard prescribes nothing, in the mirror tradition every
reading organ here keeps, because whether a monologue is a
problem is the room's call, not the instrument's.
"""

from __future__ import annotations

from loom.attribution import shares
from loom.cadence import handoffs
from loom.census import page as census_page
from loom.prose import word_count
from loom.transcript import Tape
from loom.weave import Weave


def balance(weave: Weave) -> int:
    held = shares(weave)
    if not held:
        return 0
    return max(held.values())


def page(weave: Weave, tape: Tape) -> str:
    held = shares(weave)
    lines = [
        f"session dashboard, {word_count(weave)} "
        "word(s):"
    ]
    lines.append(
        f"  rhythm: {handoffs(tape)} handoff(s) "
        "between hands"
    )
    if held:
        parts = ", ".join(
            f"{site} {held[site]}%"
            for site in sorted(
                held,
                key=lambda s: (-held[s], s),
            )
        )
        lines.append(f"  authorship: {parts}")
        top = balance(weave)
        shape = (
            "a monologue"
            if top >= 60
            else "a conversation"
        )
        lines.append(
            f"  balance: busiest hand holds {top}%, "
            f"reads as {shape}"
        )
    else:
        lines.append(
            "  authorship: an empty page owes nobody"
        )
    lines.append(
        "  fabric: "
        + census_page(weave).splitlines()[0]
    )
    lines.append(
        "the dashboard prescribes nothing; whether a "
        "monologue is a problem is the room's call"
    )
    return "\n".join(lines)
