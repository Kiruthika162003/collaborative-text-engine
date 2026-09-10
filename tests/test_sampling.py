from __future__ import annotations

from collections import Counter

import pytest

from loom.errors import Invalid
from loom.sampling import reservoir, shuffle


class TestShuffle:
    def test_it_is_a_permutation(self):
        data = list(range(20))
        result = shuffle(data, seed=1)
        assert sorted(result) == data

    def test_the_input_is_not_mutated(self):
        data = [1, 2, 3]
        shuffle(data, seed=1)
        assert data == [1, 2, 3]

    def test_deterministic_with_a_seed(self):
        assert shuffle(range(30), seed=7) == shuffle(range(30), seed=7)

    def test_empty_and_single(self):
        assert shuffle([], seed=1) == []
        assert shuffle([9], seed=1) == [9]

    def test_the_shuffle_is_roughly_uniform(self):
        # Every element should reach the first position about equally often.
        first_counts: Counter = Counter()
        for trial in range(6000):
            first_counts[shuffle([0, 1, 2], seed=trial)[0]] += 1
        for value in (0, 1, 2):
            assert 1700 < first_counts[value] < 2300


class TestReservoir:
    def test_a_larger_sample_than_the_stream_keeps_all(self):
        assert sorted(reservoir(range(3), 5, seed=1)) == [0, 1, 2]

    def test_a_zero_sample_is_empty(self):
        assert reservoir(range(10), 0, seed=1) == []

    def test_the_sample_is_a_subset_of_the_right_size(self):
        sample = reservoir(range(100), 10, seed=2)
        assert len(sample) == 10
        assert all(0 <= item < 100 for item in sample)
        assert len(set(sample)) == 10

    def test_deterministic_with_a_seed(self):
        assert reservoir(range(100), 10, seed=3) == reservoir(range(100), 10, seed=3)

    def test_a_negative_sample_is_refused(self):
        with pytest.raises(Invalid):
            reservoir(range(10), -1)

    def test_the_sample_is_roughly_uniform(self):
        # Each item of a length-5 stream should be picked about equally.
        counts: Counter = Counter()
        for trial in range(10000):
            counts[reservoir(range(5), 1, seed=trial)[0]] += 1
        for value in range(5):
            assert 1700 < counts[value] < 2300
