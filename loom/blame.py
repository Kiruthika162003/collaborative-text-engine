"""Blame: which hand wrote each line, the majority author of its surviving glyphs.

Attribution reads the document as runs of authorship down the
text; blame reads it as lines, answering the question a
reviewer asks of a collaborative draft, whose line is this.
The answer per line is the hand that contributed the most of
its surviving glyphs, because a line two people touched is
still mostly one person's, and naming the majority is more
useful than naming everyone who typed a character in it. The
count runs on the living cloth only, tombstoned glyphs
belonging to no line a reader sees, so blame reflects the
document as it stands rather than as it was drafted, which is
what a reviewer looking at the current text means. A tie, a
line split exactly between two hands, is broken toward the
alphabetically first site, an arbitrary rule chosen because it
is deterministic and stated, so two replicas blame a tied
line the same way rather than each picking whoever their
iteration happened to reach first. An empty line is blamed on
nobody, reported with a blank hand rather than forced onto a
neighbour, because a blank line is not a contribution and
attributing it would put words in a mouth that typed none.
The share and the total are both reported per line, so a
reader sees not just who won a line but how contested it was,
a line held three glyphs to two reading very differently from
one held forty to zero.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.weave import Weave


@dataclass(frozen=True)
class LineBlame:
    line: int
    site: str
    share: int
    total: int


def _verdict(line: int, counts: dict[str, int], total: int) -> LineBlame:
    if not counts:
        return LineBlame(line=line, site="", share=0, total=0)
    best = max(counts.values())
    site = min(name for name, count in counts.items() if count == best)
    return LineBlame(line=line, site=site, share=best, total=total)


def blame(weave: Weave) -> list[LineBlame]:
    result: list[LineBlame] = []
    line_no = 0
    counts: dict[str, int] = {}
    total = 0
    for strand in weave.strands:
        if strand.sheared:
            continue
        if strand.glyph == "\n":
            result.append(_verdict(line_no, counts, total))
            line_no += 1
            counts = {}
            total = 0
            continue
        counts[strand.id.site] = counts.get(strand.id.site, 0) + 1
        total += 1
    result.append(_verdict(line_no, counts, total))
    return result


def blame_of_line(weave: Weave, line: int) -> LineBlame:
    return blame(weave)[line]


def lines_by(weave: Weave, site: str) -> list[int]:
    return [row.line for row in blame(weave) if row.site == site]


def render(weave: Weave) -> str:
    rows = blame(weave)
    lines = []
    for row in rows:
        if row.site:
            lines.append(
                f"{row.line}: {row.site} ({row.share}/{row.total})"
            )
        else:
            lines.append(f"{row.line}: (blank)")
    return "\n".join(lines)
