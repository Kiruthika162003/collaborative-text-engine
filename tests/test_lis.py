from __future__ import annotations

import random

from loom.lis import lis_length, longest_increasing_subsequence


def _is_increasing_subsequence(sub: list, full: list) -> bool:
    # Strictly increasing and appears in order within full.
    if any(sub[i] >= sub[i + 1] for i in range(len(sub) - 1)):
        return False
    index = 0
    for value in full:
        if index < len(sub) and value == sub[index]:
            index += 1
    return index == len(sub)


class TestLength:
    def test_a_known_sequence(self):
        assert lis_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4

    def test_already_increasing(self):
        assert lis_length([1, 2, 3, 4, 5]) == 5

    def test_strictly_decreasing(self):
        assert lis_length([5, 4, 3, 2, 1]) == 1

    def test_empty(self):
        assert lis_length([]) == 0

    def test_duplicates_do_not_count_as_increasing(self):
        assert lis_length([2, 2, 2, 2]) == 1


class TestSubsequence:
    def test_returns_a_valid_increasing_subsequence(self):
        seq = [10, 9, 2, 5, 3, 7, 101, 18]
        sub = longest_increasing_subsequence(seq)
        assert len(sub) == 4
        assert _is_increasing_subsequence(sub, seq)

    def test_the_returned_subsequence_matches_the_length(self):
        rng = random.Random(11)
        for _ in range(50):
            seq = [rng.randrange(20) for _ in range(rng.randrange(1, 25))]
            sub = longest_increasing_subsequence(seq)
            assert len(sub) == lis_length(seq)
            assert _is_increasing_subsequence(sub, seq)

    def test_empty_sequence_gives_empty(self):
        assert longest_increasing_subsequence([]) == []
