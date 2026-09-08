from __future__ import annotations

import pytest

from loom.errors import Torn
from loom.ids import OpId
from loom.weave import HEAD, Insert, Shear
from loom.wire import (
    decode,
    decode_many,
    encode,
    encode_many,
)


def insert(
    glyph: str, origin=HEAD, counter: int = 1
) -> Insert:
    return Insert(
        id=OpId(site="alice", counter=counter),
        origin=origin,
        glyph=glyph,
        rank=counter,
    )


class TestRoundTrips:
    def test_an_insert_survives_the_wire(self):
        op = insert("a")
        line = encode(op)
        assert line == "ins|alice:1|^|1|a"
        assert decode(line) == op

    def test_an_anchored_insert_names_its_origin(self):
        op = insert(
            "b",
            origin=OpId(site="bob", counter=7),
            counter=2,
        )
        line = encode(op)
        assert "|bob:7|" in line
        assert decode(line) == op

    def test_a_shear_survives_the_wire(self):
        op = Shear(
            id=OpId(site="bob", counter=3),
            target=OpId(site="alice", counter=1),
        )
        line = encode(op)
        assert line == "shr|bob:3|alice:1"
        assert decode(line) == op

    def test_structure_cannot_be_impersonated(self):
        for tricky in ("|", "\n", "\\"):
            op = insert(tricky)
            decoded = decode(encode(op))
            assert decoded.glyph == tricky
            assert "\n" not in encode(op)

    def test_many_ops_ride_one_page(self):
        ops = [
            insert("a"),
            insert(
                "\n",
                origin=OpId(site="alice", counter=1),
                counter=2,
            ),
            Shear(
                id=OpId(site="bob", counter=1),
                target=OpId(site="alice", counter=1),
            ),
        ]
        page = encode_many(ops)
        assert len(page.split("\n")) == 3
        assert decode_many(page) == ops
        assert decode_many("") == []


class TestTornLines:
    def test_the_verbs_are_ins_and_shr(self):
        with pytest.raises(Torn) as caught:
            decode("del|alice:1|alice:2")
        assert "ins and shr" in str(caught.value)

    def test_field_counts_are_promises(self):
        with pytest.raises(Torn) as caught:
            decode("ins|alice:1|^|1")
        assert "promises compound" in str(caught.value)
        with pytest.raises(Torn):
            decode("shr|alice:1")

    def test_a_cut_off_escape_is_torn(self):
        with pytest.raises(Torn) as caught:
            decode("ins|alice:1|^|1|\\")
        assert "cut off in transit" in str(caught.value)

    def test_an_unknown_escape_is_torn(self):
        with pytest.raises(Torn):
            decode("ins|alice:1|^|1|\\z")

    def test_a_wordy_rank_is_torn(self):
        with pytest.raises(Torn):
            decode("ins|alice:1|^|first|a")


class TestGrepability:
    def test_the_eye_can_grep_a_transcript(self):
        page = encode_many(
            [
                insert("a"),
                Shear(
                    id=OpId(site="bob", counter=1),
                    target=OpId(site="alice", counter=1),
                ),
            ]
        )
        lines = page.split("\n")
        assert lines[0].startswith("ins|")
        assert lines[1].startswith("shr|")
