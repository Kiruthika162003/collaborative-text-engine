from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Invalid, Missing
from loom.invitations import InvitationDesk, Ticket


def desk() -> InvitationDesk:
    return InvitationDesk(session="draft-room")


class TestInviting:
    def test_a_ticket_binds_a_name(self):
        board = desk()
        ticket = board.invite("alice")
        assert ticket.site == "alice"
        assert len(ticket.token) == 16
        assert "alice: pending" in board.guest_list()

    def test_names_are_granted_once(self):
        board = desk()
        board.invite("alice")
        with pytest.raises(Invalid) as caught:
            board.invite("alice")
        assert "granted once" in str(caught.value)

    def test_a_bad_site_never_gets_a_ticket(self):
        with pytest.raises(Invalid):
            desk().invite("Alice")


class TestRedeeming:
    def test_a_valid_ticket_opens_the_door(self):
        board = desk()
        ticket = board.invite("alice")
        receipt = board.redeem(ticket)
        assert "seated as a writer" in receipt
        ops = Author(site="alice").type_at(0, "hi")
        for op in ops:
            assert "stands open" in board.door.screen(
                op
            )

    def test_a_second_redemption_meets_a_spent_stub(
        self,
    ):
        board = desk()
        ticket = board.invite("alice")
        board.redeem(ticket)
        with pytest.raises(Invalid) as caught:
            board.redeem(ticket)
        assert "spent stub" in str(caught.value)

    def test_a_forged_token_cannot_prove_itself(self):
        board = desk()
        board.invite("alice")
        with pytest.raises(Invalid) as caught:
            board.redeem(
                Ticket(site="alice", token="0" * 16)
            )
        assert "cannot prove itself" in str(
            caught.value
        )

    def test_a_ticketless_site_is_missing(self):
        board = desk()
        with pytest.raises(Missing):
            board.redeem(
                Ticket(site="ghost", token="x")
            )


class TestRevoking:
    def test_an_unredeemed_ticket_revokes_clean(self):
        board = desk()
        board.invite("alice")
        receipt = board.revoke("alice")
        assert "nobody was seated" in receipt

    def test_a_redeemed_ticket_demotes_through_the_door(
        self,
    ):
        board = desk()
        ticket = board.invite("alice")
        board.redeem(ticket)
        receipt = board.revoke("alice")
        assert "demoted through the door" in receipt
        with pytest.raises(Invalid):
            board.door.screen(
                Author(site="alice").type_at(0, "x")[0]
            )

    def test_the_guest_list_reads_every_state(self):
        board = desk()
        board.redeem(board.invite("alice"))
        board.invite("bob")
        board.revoke("bob")
        page = board.guest_list()
        assert "alice: redeemed" in page
        assert "bob: spent" in page
