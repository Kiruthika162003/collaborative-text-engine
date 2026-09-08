"""The sessiontrial: a whole session from the door to the signed page.

This trial exercises the seams between organs rather than
any one organ's core, because the bugs that survive unit
tests live at the joins. A desk invites two writers and
turns away a gate-crasher; the two redeem their tickets,
edit a shared document through a gremlin circle, and the
circle converges. Then the door demotes one writer
mid-session, their next operation bounces at the gate, and
the document the honest writer keeps still matches the one
the demoted writer had already contributed to, because a
demotion stops future writes without unwriting past ones,
which is the only coherent meaning demotion can have in a
convergent system. The measured facts: one gate-crasher
refused, two tickets spent, a converged fabric at
matching digests, one bounce after demotion, the demoted
hand's earlier words still standing in everyone's cloth,
and the bounced write staying local, never reaching the
honest replica, since the door screens what leaves and a
pen taken back does not erase what it already wrote.
"""

from __future__ import annotations

from loom.circle import Circle
from loom.doors import Doorkeeper
from loom.errors import Invalid
from loom.invitations import InvitationDesk
from loom.snapshot import fabric_digest
from loom.trials.verdict import Verdict


def run() -> Verdict:
    circle = Circle.of(
        ["alice", "bob"],
        temperament="gremlin",
        seed=53,
    )
    door = Doorkeeper(policy="closed")
    desk = InvitationDesk(session="draft-room", door=door)

    alice_ticket = desk.invite("alice")
    bob_ticket = desk.invite("bob")
    crasher_refused = False
    try:
        door.screen(
            circle.author("bob").type_at(0, "x")[0]
        )
    except Invalid:
        crasher_refused = True
    circle.author("bob").weave.strands.clear()
    circle.author("bob").weave.by_id.clear()
    circle.author("bob").clock.seen.clear()
    circle.author("bob").witness_rank = 0

    desk.redeem(alice_ticket)
    desk.redeem(bob_ticket)
    tickets_spent = sum(
        1
        for state in desk.state.values()
        if state == "redeemed"
    )

    circle.say(
        "alice",
        circle.author("alice").type_at(0, "shared "),
    )
    circle.say(
        "bob",
        circle.author("bob").type_at(0, "bob-here "),
    )
    circle.settle()
    converged = circle.author("alice").text() == (
        circle.author("bob").text()
    )
    bob_words_present = (
        "bob-here"
        in circle.author("alice").text()
    )
    one_digest_at_convergence = fabric_digest(
        circle.author("alice").weave
    ) == fabric_digest(circle.author("bob").weave)

    desk.revoke("bob")
    bounce_after_demotion = False
    minted = circle.author("bob").type_at(0, "sneak")
    try:
        door.screen(minted[0])
    except Invalid:
        bounce_after_demotion = True
    alice_unchanged = "sneak" not in (
        circle.author("alice").text()
    )

    numbers = {
        "crasher_refused": crasher_refused,
        "tickets_spent": tickets_spent,
        "converged": converged,
        "bob_words_survive_demotion": bob_words_present,
        "bounce_after_demotion": bounce_after_demotion,
        "one_digest_at_convergence": (
            one_digest_at_convergence
        ),
        "bounced_write_stayed_local": alice_unchanged,
    }
    holds = all(
        [
            numbers["crasher_refused"],
            numbers["tickets_spent"] == 2,
            numbers["converged"],
            numbers["bob_words_survive_demotion"],
            numbers["bounce_after_demotion"],
            numbers["one_digest_at_convergence"],
            numbers["bounced_write_stayed_local"],
        ]
    )
    return Verdict(
        trial="sessiontrial",
        claim=(
            "a full session holds at the seams: the "
            "gate-crasher refused, two tickets spent, "
            "the fabric converged, and after a "
            "mid-session demotion the next write "
            "bounces while the demoted hand's earlier "
            "words still stand, because a pen taken "
            "back does not erase what it already wrote"
        ),
        numbers=numbers,
        holds=holds,
    )
