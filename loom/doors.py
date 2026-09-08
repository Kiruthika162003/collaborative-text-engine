"""The doors: who may write, judged by hand, never by words.

Collaboration needs a no that works, and the doorkeeper is
that no: every site holds a role, writer or reader, and
screening judges the hand that minted an operation, never
its content, because a door that reads the words before
deciding is an editor, and editors pretending to be doors
is how censorship gets shipped as infrastructure. Readers
receive everything, reading being receiving, and only
their authored operations are refused, with the door named
in the refusal so the request to be promoted goes to the
right person on the first try. Strangers meet the standing
policy, an open house admitting them as writers or a
closed house holding them at the threshold, and the policy
is stated at construction rather than discovered at the
first knock. Every promotion and demotion lands in the
journal with its mover named, demotion in capitals, since
taking a pen away is the kind of act a room should
remember out loud.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid
from loom.ids import check_site
from loom.weave import Op

WRITER = "writer"
READER = "reader"
OPEN_HOUSE = "open"
CLOSED_HOUSE = "closed"


@dataclass
class Doorkeeper:
    policy: str = OPEN_HOUSE
    roles: dict[str, str] = field(default_factory=dict)
    journal: list[str] = field(default_factory=list)
    turned_away: int = 0

    def __post_init__(self) -> None:
        if self.policy not in (
            OPEN_HOUSE,
            CLOSED_HOUSE,
        ):
            raise Invalid(
                f"{self.policy!r} is not a house "
                "policy; open or closed, stated at "
                "construction"
            )

    def admit(
        self, site: str, role: str, by: str
    ) -> str:
        check_site(site)
        if role not in (WRITER, READER):
            raise Invalid(
                f"{role!r} is not a role; hands "
                "write or hands read"
            )
        former = self.roles.get(site)
        self.roles[site] = role
        if former == WRITER and role == READER:
            entry = (
                f"DEMOTED: {site} to reader by {by}; "
                "taking a pen away is remembered "
                "out loud"
            )
        else:
            entry = f"admitted: {site} as {role} by {by}"
        self.journal.append(entry)
        return entry

    def role_of(self, site: str) -> str:
        held = self.roles.get(site)
        if held is not None:
            return held
        if self.policy == OPEN_HOUSE:
            return WRITER
        return READER

    def screen(self, op: Op) -> str:
        hand = op.id.site
        role = self.role_of(hand)
        if role == WRITER:
            return f"{hand} writes; the door stands open"
        self.turned_away += 1
        raise Invalid(
            f"{op.id.wire()} refused at the door: "
            f"{hand} holds a reader's role"
            + (
                ""
                if hand in self.roles
                else " under the closed-house policy"
            )
            + "; the door judges hands, not words"
        )

    def page(self) -> str:
        lines = [
            f"a {self.policy} house, "
            f"{len(self.roles)} named role(s), "
            f"{self.turned_away} turned away"
        ]
        for site in sorted(self.roles):
            lines.append(
                f"  {site}: {self.roles[site]}"
            )
        lines.extend(
            f"  {entry}"
            for entry in self.journal
            if entry.startswith("DEMOTED")
        )
        return "\n".join(lines)
