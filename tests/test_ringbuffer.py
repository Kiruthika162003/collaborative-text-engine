from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.ringbuffer import RingBuffer


class TestFill:
    def test_it_holds_items_up_to_capacity(self):
        buffer = RingBuffer(3)
        for value in [1, 2, 3]:
            buffer.push(value)
        assert buffer.items() == [1, 2, 3]

    def test_it_is_not_full_before_capacity(self):
        buffer = RingBuffer(3)
        buffer.push(1)
        assert not buffer.is_full()

    def test_it_is_full_at_capacity(self):
        buffer = RingBuffer(2)
        buffer.push(1)
        buffer.push(2)
        assert buffer.is_full()


class TestOverwrite:
    def test_the_oldest_is_dropped(self):
        buffer = RingBuffer(3)
        for value in [1, 2, 3, 4]:
            buffer.push(value)
        assert buffer.items() == [2, 3, 4]

    def test_it_keeps_the_last_capacity_items(self):
        buffer = RingBuffer(3)
        for value in range(1, 7):
            buffer.push(value)
        assert buffer.items() == [4, 5, 6]

    def test_length_never_exceeds_capacity(self):
        buffer = RingBuffer(2)
        for value in range(10):
            buffer.push(value)
        assert len(buffer) == 2


class TestGuards:
    def test_a_zero_capacity_is_refused(self):
        with pytest.raises(Invalid):
            RingBuffer(0)
