"""The citetrial: citation numbers read position, so two replicas cannot disagree.

Citation numbering looks like it should be order-sensitive:
the first source cited gets one, the second gets two, and if
two authors cite in different orders the numbers ought to
diverge. That was the guess this trial set out to confirm,
and the measurement refuted it. The numbers are assigned by
first appearance in reading order, not by the order the
citations were added, so this trial has two authors converge
on the same text and then add the same four citations in
opposite orders, alice front to back and bob back to front,
and measures whether their works-cited lists match. They
match, four distinct sources numbered one through four the
same way on both replicas, because the numbering reads the
one thing a converged fabric agrees on completely, the
position of every strand, and the order a local author
happened to click the cite button leaves no trace in a
number computed from position. The bibliographies are built
by merging two authors' private source lists, so the trial
also exercises the union that a shared reference list must
survive, and the count of distinct sources is measured
rather than assumed so a merge that silently dropped or
duplicated a source would show as a number that is not four.
"""

from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.citations import Bibliography, Citation, Citations, Source
from loom.ids import OpId
from loom.trials.verdict import Verdict

SOURCES = (
    Source(key="smith", author="Smith", title="On Weaving", year=2020),
    Source(key="patel", author="Patel", title="On Anchors", year=2021),
    Source(key="jones", author="Jones", title="On Merging", year=2019),
    Source(key="ng", author="Ng", title="On Pins", year=2022),
)


def _bibliography() -> Bibliography:
    left = Bibliography()
    left.enter(SOURCES[0])
    left.enter(SOURCES[1])
    right = Bibliography()
    right.enter(SOURCES[2])
    right.enter(SOURCES[3])
    return left.merge(right)


def _anchor(author: Author, visible: int) -> OpId:
    return author.weave.strand_at_visible(visible).id


def _placements(author: Author) -> list[tuple[str, OpId]]:
    return [
        ("smith", _anchor(author, 0)),
        ("patel", _anchor(author, 3)),
        ("jones", _anchor(author, 6)),
        ("ng", _anchor(author, 9)),
    ]


def run() -> Verdict:
    circle = Circle.of(["alice", "bob"])
    ops = circle.author("alice").type_at(0, "aa bb cc dd")
    circle.say("alice", ops)
    circle.settle()

    biblio = _bibliography()
    alice = circle.author("alice")
    bob = circle.author("bob")

    alice_marks = Citations(weave=alice.weave, bibliography=biblio)
    for order, (key, anchor) in enumerate(_placements(alice), start=1):
        alice_marks.cite(Citation(OpId("alice", order), anchor, key))

    bob_marks = Citations(weave=bob.weave, bibliography=biblio)
    for order, (key, anchor) in enumerate(
        reversed(_placements(bob)), start=1
    ):
        bob_marks.cite(Citation(OpId("bob", order), anchor, key))

    numbers = {
        "distinct_sources": len(alice_marks.order()),
        "total_marks": len(alice_marks.marks),
        "same_numbering": alice_marks.numbering()
        == bob_marks.numbering(),
        "same_works_cited": alice_marks.works_cited()
        == bob_marks.works_cited(),
    }
    holds = (
        numbers["same_numbering"]
        and numbers["same_works_cited"]
        and numbers["distinct_sources"] == 4
    )
    return Verdict(
        trial="citetrial",
        claim=(
            "citation numbers are assigned by first appearance "
            "in reading order, so two replicas that converged "
            "number the same citations identically no matter "
            "the order each author added them, because the "
            "numbering reads position and position is the one "
            "thing a converged fabric fully agrees on"
        ),
        numbers=numbers,
        holds=holds,
    )
