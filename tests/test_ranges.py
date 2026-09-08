from __future__ import annotations

from loom.author import Author
from loom.ranges import Reservations


def reserved() -> tuple[Author, Reservations, list]:
    author = Author(site="alice")
    ops = author.type_at(0, "the reserved section here")
    res = Reservations(weave=author.weave)
    res.reserve("alice", ops[4].id, ops[11].id)
    return author, res, ops


class TestChecking:
    def test_others_are_warned_inside_the_lock(self):
        _author, res, ops = reserved()
        message = res.check("bob", ops[6].id)
        assert "should coordinate with alice" in message
        assert "names whom to ask" in message

    def test_the_holder_edits_freely(self):
        _author, res, ops = reserved()
        assert "may edit here" in res.check(
            "alice", ops[6].id
        )

    def test_outside_the_lock_is_open(self):
        _author, res, ops = reserved()
        assert "may edit here" in res.check(
            "bob", ops[20].id
        )

    def test_stacked_locks_name_every_holder(self):
        _author, res, ops = reserved()
        res.reserve("cara", ops[3].id, ops[10].id)
        holders = res.holders_at(ops[6].id, "bob")
        assert holders == ["alice", "cara"]


class TestLifecycle:
    def test_the_lock_follows_moving_text(self):
        author, res, ops = reserved()
        author.type_at(0, ">>> ")
        assert "should coordinate" in res.check(
            "bob", ops[6].id
        )

    def test_a_lock_over_a_grave_expires(self):
        author, res, ops = reserved()
        author.erase_at(4, 8)
        assert len(res.expired()) == 1
        assert "may edit here" in res.check(
            "bob", ops[20].id
        )

    def test_the_report_counts_live_and_expired(self):
        _author, res, _ops = reserved()
        page = res.report()
        assert "1 live reservation(s)" in page
        assert "held by alice" in page
