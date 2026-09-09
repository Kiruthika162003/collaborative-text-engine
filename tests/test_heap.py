from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.heap import MinHeap, heapsort


class TestHeap:
    def test_pop_yields_smallest_first(self):
        heap = MinHeap()
        for value in [3, 1, 2]:
            heap.push(value)
        assert [heap.pop(), heap.pop(), heap.pop()] == [1, 2, 3]

    def test_peek_shows_the_minimum(self):
        heap = MinHeap()
        heap.push(5)
        heap.push(2)
        assert heap.peek() == 2

    def test_length_tracks_pushes_and_pops(self):
        heap = MinHeap()
        heap.push(1)
        heap.push(2)
        heap.pop()
        assert len(heap) == 1

    def test_pop_empty_is_refused(self):
        with pytest.raises(Invalid):
            MinHeap().pop()

    def test_peek_empty_is_refused(self):
        with pytest.raises(Invalid):
            MinHeap().peek()


class TestHeapsort:
    def test_it_sorts(self):
        assert heapsort([5, 3, 8, 1, 9, 2]) == [1, 2, 3, 5, 8, 9]

    def test_duplicates_survive(self):
        assert heapsort([2, 1, 2, 1]) == [1, 1, 2, 2]

    def test_an_empty_list(self):
        assert heapsort([]) == []
