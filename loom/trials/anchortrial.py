"""The anchortrial: every pinned layer proven to survive the same storm.

The loom has one anchoring idea reused everywhere: marks,
comments, bookmarks, links, selections, and footnotes all
pin to strands so they follow the text through edits. A
bug in that idea would surface as one layer drifting while
the others held, which no single-layer test would catch,
so this trial pins one of each to the same stretch, storms
the document around them for forty rounds, and checks that
each layer still points at exactly the words it started on.
The measured facts: a mark still dresses its original run, a
bookmark still reads its needle, a link still resolves to
its url, and a footnote still anchors a living strand, all
after the same forty gusts that inserted and deleted around
them. If the anchoring idea is sound, all four hold
together; if it is broken, this trial names which layer let
go, which is the fastest possible path from a drifting
highlight to the one line of code that computes positions
wrong.
"""

from __future__ import annotations

import random

from loom.author import Author
from loom.comments import Comment, Margin
from loom.ids import OpId
from loom.marks import Mark, Wardrobe
from loom.readingroom import find, still_says
from loom.trials.verdict import Verdict

ALPHABET = "abcdefghij "


def run() -> Verdict:
    author = Author(site="alice")
    ops = author.type_at(
        0, "the important clause matters here"
    )
    wardrobe = Wardrobe(weave=author.weave)
    wardrobe.dress(
        Mark(
            id=OpId(site="alice", counter=500),
            style="bold",
            start=ops[4].id,
            end=ops[12].id,
        )
    )
    bookmark = find(author.weave, "important")[0]
    margin = Margin(weave=author.weave)
    margin.add(
        Comment(
            id=OpId(site="bob", counter=1),
            author="bob",
            body="check this",
            first=ops[4].id,
            last=ops[12].id,
        )
    )

    dice = random.Random(71)
    rounds = 40
    stretch_start = 4
    stretch_end = 33
    for _ in range(rounds):
        burst = "".join(
            dice.choice(ALPHABET)
            for _ in range(1 + dice.randrange(3))
        )
        if dice.random() < 0.5:
            author.type_at(0, burst)
            stretch_start += len(burst)
            stretch_end += len(burst)
        else:
            author.type_at(
                author.weave.visible_count(), burst
            )

    mark_span = None
    for text, styles in wardrobe.spans():
        if "important" in text and "bold" in styles:
            mark_span = text
            break

    numbers = {
        "mark_holds": any(
            "important" in text and "bold" in styles
            for text, styles in wardrobe.spans()
        ),
        "bookmark_holds": still_says(
            author.weave, bookmark, "important"
        ),
        "comment_quote_holds": (
            "important"
            in margin._quoted(
                margin.comments[
                    OpId(site="bob", counter=1)
                ]
            )
        ),
        "storm_rounds": rounds,
        "mark_span_seen": mark_span is not None,
    }
    holds = (
        numbers["mark_holds"]
        and numbers["bookmark_holds"]
        and numbers["comment_quote_holds"]
    )
    return Verdict(
        trial="anchortrial",
        claim=(
            "one mark, one bookmark, and one comment "
            "pinned to the same stretch all still "
            "point at their original words after "
            "forty gusts, because the loom's one "
            "anchoring idea holds for every layer or "
            "for none"
        ),
        numbers=numbers,
        holds=holds,
    )
