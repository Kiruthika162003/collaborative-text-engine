"""Horspool: search from the pattern's end and skip ahead by what the text reveals.

Boyer-Moore-Horspool searches for a pattern by comparing it to the
text from the pattern's last character backward toward its first,
which sounds pointless, since a mismatch anywhere still fails the
whole alignment, but the direction is what makes the jumps large.
When an alignment fails, the algorithm looks at the text character
currently lined up with the pattern's last position and asks where
that character appears in the pattern; it then slides the pattern
forward just far enough to bring that character's rightmost
occurrence in the pattern under where it sits in the text, because
any smaller slide would leave a character the pattern cannot match
there and so cannot possibly align. If the character does not
appear in the pattern at all, the pattern slides clear past it, a
jump of its whole length. So a single look at one text character
can skip over several positions without ever inspecting them, and
on a large alphabet, where most text characters do not appear in
the pattern, the search examines far fewer characters than it
passes, running sublinearly in the happy case. I had guessed
scanning from the end could not help, that a mismatch was a
mismatch whichever way you read it; the help is not in detecting
the mismatch faster but in the skip the end character licenses,
which the forward scan cannot compute because it does not yet know
what sits at the far end of the alignment. The honest boundary is
the worst case: on a small alphabet or a pattern of repeated
characters the skips shrink to one and Horspool degrades to the
same product of lengths the naive scan pays, so its advantage is a
best and average case, not a guarantee like the prefix-table
search gives. The skip table is built once from the pattern before
the search, mapping each of its characters except the last to how
far the pattern would slide, and it reports every match including
overlaps by stepping one position past a found match, matching the
convention the other searches here use.
"""

from __future__ import annotations


def _skip_table(pattern: str) -> dict:
    span = len(pattern)
    table: dict = {}
    for index in range(span - 1):
        table[pattern[index]] = span - 1 - index
    return table


def search(text: str, pattern: str) -> list[int]:
    text_length = len(text)
    span = len(pattern)
    if pattern == "":
        return list(range(text_length + 1))
    if span > text_length:
        return []
    table = _skip_table(pattern)
    matches = []
    window = 0
    while window <= text_length - span:
        cursor = span - 1
        while cursor >= 0 and text[window + cursor] == pattern[cursor]:
            cursor -= 1
        if cursor < 0:
            matches.append(window)
            window += 1
        else:
            window += table.get(text[window + span - 1], span)
    return matches


def first(text: str, pattern: str) -> int:
    found = search(text, pattern)
    return found[0] if found else -1


def contains(text: str, pattern: str) -> bool:
    return bool(search(text, pattern))
