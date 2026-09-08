"""Attribution: who wrote the surviving text, and who held the scissors.

Every strand carries its author in its id, so attribution
here is not detective work but a census, and the census
reads only the surviving text: the dead do not count
toward authorship, because the sentence you deleted is
not part of what you wrote, it is part of what you
decided against. The byline walks the visible fabric and
folds consecutive same-hand glyphs into runs, which is
how collaboration actually reads, paragraphs of one voice
seamed to paragraphs of another. Shares are percentages
that sum to one hundred by largest remainder, a column
that sums to ninety-eight sending every reader hunting
for the missing two. The scissors census is separate and
deliberate: erasure is real work and its own kind of
authorship, counted by shear operations seen, double cuts
included, since deciding a thing twice is still deciding.
"""

from __future__ import annotations

from loom.weave import Weave


def who_wrote(
    weave: Weave,
) -> list[tuple[str, str]]:
    return [
        (strand.glyph, strand.id.site)
        for strand in weave.strands
        if not strand.sheared
    ]


def byline(weave: Weave) -> list[tuple[str, str]]:
    runs: list[tuple[str, str]] = []
    for glyph, site in who_wrote(weave):
        if runs and runs[-1][1] == site:
            runs[-1] = (runs[-1][0] + glyph, site)
        else:
            runs.append((glyph, site))
    return runs


def shares(weave: Weave) -> dict[str, int]:
    counts: dict[str, int] = {}
    for _glyph, site in who_wrote(weave):
        counts[site] = counts.get(site, 0) + 1
    total = sum(counts.values())
    if total == 0:
        return {}
    exact = {
        site: count * 100 / total
        for site, count in counts.items()
    }
    floored = {
        site: int(value)
        for site, value in exact.items()
    }
    leftover = 100 - sum(floored.values())
    by_remainder = sorted(
        exact,
        key=lambda site: (
            -(exact[site] - floored[site]),
            site,
        ),
    )
    for site in by_remainder[:leftover]:
        floored[site] += 1
    return floored


def scissors(weave: Weave) -> dict[str, int]:
    counts: dict[str, int] = {}
    for shear_id in weave.shears_seen:
        counts[shear_id.site] = (
            counts.get(shear_id.site, 0) + 1
        )
    return counts


def page(weave: Weave) -> str:
    runs = byline(weave)
    if not runs:
        return (
            "an empty cloth; nobody has written, "
            "nobody is owed"
        )
    lines = [f"{len(runs)} run(s) of voice:"]
    for text, site in runs:
        shown = text if len(text) <= 24 else (
            text[:21] + "..."
        )
        lines.append(f"  {site}: {shown!r}")
    held = shares(weave)
    for site in sorted(
        held, key=lambda name: (-held[name], name)
    ):
        lines.append(f"  {site} wrote {held[site]}%")
    cut = scissors(weave)
    for site in sorted(cut):
        lines.append(
            f"  {site} cut {cut[site]} time(s); "
            "erasure is its own kind of authorship"
        )
    lines.append(
        "the dead do not count toward authorship; "
        "what you deleted is what you decided against"
    )
    return "\n".join(lines)
