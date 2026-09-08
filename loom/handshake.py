"""The handshake: two clocks compared, two gaps filled, receipts kept.

Anti-entropy is the politest protocol in distributed
systems: show me your clock, here is everything it lacks,
now show me yours. The handshake runs that exchange both
ways and repeats until the two clocks read identically,
which normally takes one round and is allowed a few more
because operations shipped in round one can unshelve
arrivals whose absence hid further gaps. A shake that
fails to settle within its allowance raises rather than
loops, anti-entropy that never settles being entropy with
a schedule, and the receipt itemizes what crossed in each
direction because the bill is the point: the whole reason
deltas exist is that shipping everything every time is a
sync strategy for people who have never paid for a
network. A shake between already-equal clocks ships
nothing and says so in one word, peace, the cheapest
receipt this codebase issues.
"""

from __future__ import annotations

from loom.errors import Diverged
from loom.station import Station

SETTLE_ALLOWANCE = 4


def shake(
    left: Station, right: Station
) -> str:
    if left.clock().wire() == right.clock().wire():
        return (
            f"{left.site} and {right.site}: peace; "
            "nothing to ship"
        )
    shipped_to_right = 0
    shipped_to_left = 0
    rounds = 0
    while (
        left.clock().wire() != right.clock().wire()
    ):
        rounds += 1
        if rounds > SETTLE_ALLOWANCE:
            raise Diverged(
                f"{left.site} and {right.site} did "
                f"not settle in {SETTLE_ALLOWANCE} "
                "round(s); anti-entropy that never "
                "settles is entropy with a schedule"
            )
        for op in left.ops_missing_for(right.clock()):
            right.hear(op)
            shipped_to_right += 1
        for op in right.ops_missing_for(left.clock()):
            left.hear(op)
            shipped_to_left += 1
    return (
        f"settled in {rounds} round(s): "
        f"{shipped_to_right} op(s) to {right.site}, "
        f"{shipped_to_left} op(s) to {left.site}"
    )


def gossip(stations: list[Station]) -> str:
    """One full round of pairwise shakes, every pair once."""
    receipts = []
    for index, left in enumerate(stations):
        for right in stations[index + 1:]:
            receipts.append(shake(left, right))
    return "\n".join(receipts)
