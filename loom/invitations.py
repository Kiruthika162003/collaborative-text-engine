"""Invitations: names granted once, tickets checked, the door pre-signed.

Site names are load-bearing everywhere, in ids, in
tiebreaks, in journals, so a session cannot let two hands
answer to one name, and the invitation desk is where that
uniqueness is enforced before the first keystroke rather
than discovered after divergence. Inviting a site mints a
ticket, a single-use token bound to that name; redeeming
the ticket admits the site through the doorkeeper as a
writer and spends the token, so a leaked ticket forged
into a second redemption meets a spent stub, not an open
door. Names are granted once: inviting a site already
seated is refused, because the second invitation is
either a mistake or an attack and neither deserves a
yes. Revoking an unredeemed ticket is clean, revoking a
redeemed one demotes the seated hand through the door and
says so, and the ledger names every ticket's state, since
a guest list nobody can read is a guest list that admits
everyone.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from loom.doors import Doorkeeper
from loom.errors import Invalid, Missing
from loom.ids import check_site

TICKET_PENDING = "pending"
TICKET_REDEEMED = "redeemed"
TICKET_SPENT = "spent"


def _mint_token(session: str, site: str) -> str:
    return hashlib.sha256(
        f"{session}|{site}".encode()
    ).hexdigest()[:16]


@dataclass(frozen=True)
class Ticket:
    site: str
    token: str


@dataclass
class InvitationDesk:
    session: str
    door: Doorkeeper = field(
        default_factory=lambda: Doorkeeper(
            policy="closed"
        )
    )
    tickets: dict[str, str] = field(
        default_factory=dict
    )
    state: dict[str, str] = field(default_factory=dict)

    def invite(self, site: str) -> Ticket:
        check_site(site)
        if site in self.tickets:
            raise Invalid(
                f"{site} already has a ticket in "
                f"state {self.state[site]!r}; names "
                "are granted once, and the second "
                "invitation is a mistake or an attack"
            )
        token = _mint_token(self.session, site)
        self.tickets[site] = token
        self.state[site] = TICKET_PENDING
        return Ticket(site=site, token=token)

    def redeem(self, ticket: Ticket) -> str:
        held = self.tickets.get(ticket.site)
        if held is None:
            raise Missing(
                f"{ticket.site} holds no ticket to "
                "this session"
            )
        if self.state[ticket.site] != TICKET_PENDING:
            raise Invalid(
                f"{ticket.site}'s ticket is "
                f"{self.state[ticket.site]}; a leaked "
                "ticket forged into a second "
                "redemption meets a spent stub, not "
                "an open door"
            )
        if held != ticket.token:
            raise Invalid(
                f"{ticket.site}'s token does not "
                "match the desk's; a ticket that "
                "cannot prove itself is a rumor"
            )
        self.door.admit(
            ticket.site, "writer", by=self.session
        )
        self.state[ticket.site] = TICKET_REDEEMED
        return (
            f"{ticket.site} seated as a writer; the "
            "ticket is spent"
        )

    def revoke(self, site: str) -> str:
        if site not in self.tickets:
            raise Missing(
                f"{site} holds no ticket to revoke"
            )
        was = self.state[site]
        self.state[site] = TICKET_SPENT
        if was == TICKET_REDEEMED:
            self.door.admit(
                site, "reader", by=self.session
            )
            return (
                f"{site} revoked and demoted through "
                "the door; a pen taken back is "
                "remembered out loud"
            )
        return (
            f"{site}'s unredeemed ticket revoked; "
            "clean, nobody was seated"
        )

    def guest_list(self) -> str:
        if not self.tickets:
            return (
                f"session {self.session}: no "
                "invitations yet"
            )
        lines = [
            f"session {self.session}, "
            f"{len(self.tickets)} ticket(s):"
        ]
        for site in sorted(self.tickets):
            lines.append(
                f"  {site}: {self.state[site]}"
            )
        return "\n".join(lines)
