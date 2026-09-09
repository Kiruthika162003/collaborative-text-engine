"""Three-way merge: combine two edits of a common base, marking only the true conflicts.

The loom's own replicas merge without markers, but text that
left the loom and was edited in two places offline needs the
classic three-way merge: given the base both started from and
the two edited versions, produce one text that carries both
sets of changes, falling back to conflict markers only where
the two edits touched the same region differently. This does
it at the line level. It aligns each edited version to the
base, finds the lines common to all three as sync anchors, and
between anchors looks at what each side did to that region: if
only one side changed it, that side's version is taken; if
both made the same change, it is taken once; and only if both
changed it to different things is a conflict raised, wrapped in
the same seven-bracket markers the conflict-markers module
knows how to resolve, so a merge that conflicts hands its
output straight to the tool that settles it. The three short-
circuits come first and matter: if one side did not change the
base at all, the other side's version is the answer whole,
which is the common case of one person editing while the other
left the file alone. The granularity is the line, stated
plainly: two edits to different words of the same line are a
conflict here, not a clever word-level splice, because merging
inside a line invites the subtle corruption a line-level merge
cannot make, and a conflict a human resolves is safer than a
splice a tool got wrong.
"""

from __future__ import annotations

import difflib

OURS_MARK = "<<<<<<< ours"
DIVIDER = "======="
THEIRS_MARK = ">>>>>>> theirs"


def _line_map(base: list[str], other: list[str]) -> dict[int, int]:
    mapping: dict[int, int] = {}
    matcher = difflib.SequenceMatcher(a=base, b=other, autojunk=False)
    for base_i, other_j, size in matcher.get_matching_blocks():
        for step in range(size):
            mapping[base_i + step] = other_j + step
    return mapping


def merge3(base: str, ours: str, theirs: str) -> tuple[str, bool]:
    if ours == base:
        return theirs, False
    if theirs == base:
        return ours, False
    if ours == theirs:
        return ours, False

    base_lines = base.split("\n")
    ours_lines = ours.split("\n")
    theirs_lines = theirs.split("\n")
    to_ours = _line_map(base_lines, ours_lines)
    to_theirs = _line_map(base_lines, theirs_lines)
    anchors = sorted(set(to_ours) & set(to_theirs))

    result: list[str] = []
    conflict = False
    prev_b = prev_o = prev_t = -1
    for base_i in [*anchors, len(base_lines)]:
        if base_i == len(base_lines):
            ours_j, theirs_j = len(ours_lines), len(theirs_lines)
        else:
            ours_j, theirs_j = to_ours[base_i], to_theirs[base_i]
        base_seg = base_lines[prev_b + 1 : base_i]
        ours_seg = ours_lines[prev_o + 1 : ours_j]
        theirs_seg = theirs_lines[prev_t + 1 : theirs_j]
        if ours_seg == base_seg:
            result.extend(theirs_seg)
        elif theirs_seg in (base_seg, ours_seg):
            result.extend(ours_seg)
        else:
            conflict = True
            result.append(OURS_MARK)
            result.extend(ours_seg)
            result.append(DIVIDER)
            result.extend(theirs_seg)
            result.append(THEIRS_MARK)
        if base_i < len(base_lines):
            result.append(base_lines[base_i])
        prev_b, prev_o, prev_t = base_i, ours_j, theirs_j
    return "\n".join(result), conflict


def conflicts(base: str, ours: str, theirs: str) -> bool:
    return merge3(base, ours, theirs)[1]
