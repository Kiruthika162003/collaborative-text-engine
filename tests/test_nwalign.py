from __future__ import annotations

import random

from loom.nwalign import GAP, align, score_of


def _ungap(aligned: str) -> str:
    return aligned.replace(GAP, "")


class TestAlignment:
    def test_identical_sequences_align_without_gaps(self):
        top, bottom, points = align("GATTACA", "GATTACA")
        assert top == "GATTACA"
        assert bottom == "GATTACA"
        assert points == 7

    def test_a_single_gap(self):
        top, bottom, _ = align("GATTACA", "GATTCA")
        assert _ungap(top) == "GATTACA"
        assert _ungap(bottom) == "GATTCA"
        assert len(top) == len(bottom)

    def test_the_two_rows_are_equal_length(self):
        top, bottom, _ = align("the quick fox", "a quick brown fox")
        assert len(top) == len(bottom)

    def test_dropping_gaps_recovers_the_originals(self):
        rng = random.Random(9)
        for _ in range(200):
            a = "".join(rng.choice("ACGT") for _ in range(rng.randint(0, 15)))
            b = "".join(rng.choice("ACGT") for _ in range(rng.randint(0, 15)))
            top, bottom, _ = align(a, b)
            assert _ungap(top) == a
            assert _ungap(bottom) == b


class TestScore:
    def test_a_mismatch_costs_less_than_a_match(self):
        assert score_of("AAAA", "AAAA") > score_of("AAAA", "AATA")

    def test_empty_against_a_sequence_is_all_gaps(self):
        top, bottom, points = align("", "ACGT")
        assert top == GAP * 4
        assert bottom == "ACGT"
        assert points == -4

    def test_custom_penalties_change_the_score(self):
        cheap_gap = score_of("AC", "AGC", gap=-1)
        dear_gap = score_of("AC", "AGC", gap=-5)
        assert cheap_gap > dear_gap
