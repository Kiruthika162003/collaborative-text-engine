from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Invalid
from loom.mailroom import Mailroom
from loom.throttle import TokenBucket


def some_ops(count: int):
    author = Author(site="alice")
    return author.type_at(0, "x" * count)


class TestPacing:
    def test_a_burst_ships_up_to_the_cap(self):
        bucket = TokenBucket(rate=1.0, cap=3.0)
        bucket.offer_many(some_ops(5))
        shipped = bucket.drain()
        assert len(shipped) == 3
        assert len(bucket.waiting) == 2

    def test_the_rest_waits_not_drops(self):
        bucket = TokenBucket(rate=1.0, cap=3.0)
        ops = some_ops(5)
        bucket.offer_many(ops)
        bucket.drain()
        bucket.advance(2)
        more = bucket.drain()
        assert len(more) == 2
        assert bucket.waiting == []
        assert bucket.shipped == 5

    def test_nothing_ships_when_the_bucket_is_dry(self):
        bucket = TokenBucket(rate=1.0, cap=2.0)
        bucket.offer_many(some_ops(2))
        bucket.drain()
        bucket.offer_many(some_ops(1))
        assert bucket.drain() == []

    def test_the_bucket_caps_its_own_fill(self):
        bucket = TokenBucket(rate=1.0, cap=3.0)
        bucket.drain()
        bucket.advance(100)
        assert bucket.tokens == 3.0


class TestGuards:
    def test_a_backward_clock_is_refused(self):
        bucket = TokenBucket(rate=1.0, cap=2.0)
        bucket.advance(5)
        with pytest.raises(Invalid):
            bucket.advance(2)

    def test_a_rateless_bucket_is_refused(self):
        with pytest.raises(Invalid):
            TokenBucket(rate=0.0, cap=2.0)


class TestConvergence:
    def test_paced_delivery_still_converges(self):
        author = Author(site="alice")
        ops = author.type_at(0, "convergent")
        bob = Author(site="bob")
        room = Mailroom(author=bob)
        bucket = TokenBucket(rate=2.0, cap=2.0)
        bucket.offer_many(ops)
        tick = 0
        while bucket.waiting or bucket.tokens >= 1:
            for op in bucket.drain():
                room.receive(op)
            if not bucket.waiting:
                break
            tick += 1
            bucket.advance(tick)
        assert bob.text() == "convergent"

    def test_the_report_names_both_numbers(self):
        bucket = TokenBucket(rate=1.0, cap=2.0)
        bucket.offer_many(some_ops(5))
        bucket.drain()
        page = bucket.report()
        assert "token(s) available" in page
        assert "op(s) waiting" in page
        assert "delayed never dropped" in page
