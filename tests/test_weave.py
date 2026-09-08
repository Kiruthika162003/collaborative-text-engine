from __future__ import annotations

import pytest

from loom.errors import Invalid, Missing
from loom.ids import OpId
from loom.weave import HEAD, Insert, Shear, Weave


def op_id(site: str, counter: int) -> OpId:
    return OpId(site=site, counter=counter)


def typed_run(
    site: str, start: int, text: str, origin=HEAD
) -> list[Insert]:
    ops = []
    anchor = origin
    for offset, glyph in enumerate(text):
        this_id = op_id(site, start + offset)
        ops.append(
            Insert(id=this_id, origin=anchor, glyph=glyph)
        )
        anchor = this_id
    return ops


class TestWeaving:
    def test_a_run_reads_back_in_order(self):
        weave = Weave()
        for op in typed_run("alice", 1, "hello"):
            weave.apply(op)
        assert weave.text() == "hello"

    def test_apply_is_idempotent(self):
        weave = Weave()
        ops = typed_run("alice", 1, "hi")
        for op in ops:
            weave.apply(op)
        receipt = weave.apply(ops[0])
        assert "weaves once" in receipt
        assert weave.text() == "hi"

    def test_an_unseen_origin_is_a_buffer_cue(self):
        weave = Weave()
        with pytest.raises(Missing) as caught:
            weave.apply(
                Insert(
                    id=op_id("bob", 2),
                    origin=op_id("bob", 1),
                    glyph="x",
                )
            )
        assert "Buffer it" in str(caught.value)

    def test_strands_carry_one_glyph(self):
        with pytest.raises(Invalid):
            Insert(
                id=op_id("alice", 1),
                origin=HEAD,
                glyph="ab",
            )


class TestConcurrency:
    def test_runs_do_not_interleave(self):
        alice_ops = typed_run("alice", 1, "abc")
        bob_ops = typed_run("bob", 1, "xyz")
        one = Weave()
        for op in alice_ops + bob_ops:
            one.apply(op)
        two = Weave()
        for op in bob_ops + alice_ops:
            two.apply(op)
        assert one.text() == two.text()
        assert one.text() in ("abcxyz", "xyzabc")

    def test_the_higher_id_stands_closer(self):
        first = Insert(
            id=op_id("alice", 1), origin=HEAD, glyph="a"
        )
        second = Insert(
            id=op_id("bob", 1), origin=HEAD, glyph="b"
        )
        weave = Weave()
        weave.apply(first)
        weave.apply(second)
        assert weave.text() == "ba"

    def test_siblings_rank_below_the_resident_run(self):
        weave = Weave()
        alice_ops = typed_run("alice", 1, "ad")
        for op in alice_ops:
            weave.apply(op)
        weave.apply(
            Insert(
                id=op_id("bob", 1),
                origin=alice_ops[0].id,
                glyph="c",
            )
        )
        weave.apply(
            Insert(
                id=op_id("cara", 1),
                origin=alice_ops[0].id,
                glyph="b",
            )
        )
        assert weave.text() == "adbc"


class TestShears:
    def test_the_text_hides_what_the_fabric_keeps(self):
        weave = Weave()
        ops = typed_run("alice", 1, "abc")
        for op in ops:
            weave.apply(op)
        weave.apply(
            Shear(id=op_id("bob", 1), target=ops[1].id)
        )
        assert weave.text() == "ac"
        assert weave.visible_count() == 2
        assert weave.tombstone_count() == 1

    def test_two_scissors_one_cut(self):
        weave = Weave()
        ops = typed_run("alice", 1, "ab")
        for op in ops:
            weave.apply(op)
        weave.apply(
            Shear(id=op_id("bob", 1), target=ops[0].id)
        )
        receipt = weave.apply(
            Shear(id=op_id("cara", 1), target=ops[0].id)
        )
        assert "two scissors, one cut" in receipt
        assert weave.tombstone_count() == 1

    def test_a_tombstone_still_anchors_arrivals(self):
        weave = Weave()
        ops = typed_run("alice", 1, "ab")
        for op in ops:
            weave.apply(op)
        weave.apply(
            Shear(id=op_id("bob", 1), target=ops[0].id)
        )
        weave.apply(
            Insert(
                id=op_id("cara", 1),
                origin=ops[0].id,
                glyph="x",
            )
        )
        assert weave.text() == "bx"


class TestVisibleAddressing:
    def test_visible_indexes_skip_tombstones(self):
        weave = Weave()
        ops = typed_run("alice", 1, "abc")
        for op in ops:
            weave.apply(op)
        weave.apply(
            Shear(id=op_id("bob", 1), target=ops[0].id)
        )
        assert weave.strand_at_visible(0).glyph == "b"
        assert weave.origin_for_insert_at(0) is HEAD
        assert (
            weave.origin_for_insert_at(1) == ops[1].id
        )

    def test_past_the_cloth_is_named(self):
        weave = Weave()
        for op in typed_run("alice", 1, "ab"):
            weave.apply(op)
        with pytest.raises(Missing) as caught:
            weave.strand_at_visible(5)
        assert "past the cloth" in str(caught.value)
