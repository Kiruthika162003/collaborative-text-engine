"""KMP: find a pattern in text without ever re-reading a character, by a prefix table.

The naive way to find a pattern in text lines the pattern up at
each position and compares forward until it matches or mismatches,
and on a mismatch it slides the pattern one step and starts the
comparison over from the beginning, which re-reads the text
characters it already looked at. Knuth-Morris-Pratt removes that
re-reading. Before the search it studies the pattern alone and
builds a table that says, for each prefix of the pattern, how much
of that prefix is also a suffix of it, the longest border. When a
mismatch happens partway into a match, that table says how far the
pattern can slide without missing a possible match, because the
part already matched is known and its borders are the only places a
new match could pick up, so the search jumps the pattern forward by
that much and, crucially, never moves the text cursor backward. The
text is read once, left to right, each character examined a bounded
number of times, so the search is linear in the text plus the
pattern no matter how the two are shaped. I had guessed the naive
scan and this would find a substring about equally often in
practice and that the table was mostly theory; on ordinary prose
they very nearly tie, because prose almost never makes the naive
scan re-read much, and KMP's advantage shows only on inputs built
from long repeated prefixes, the pathological case a search over
real text rarely meets. So the table earns its keep as insurance
against the adversarial input rather than as a speedup on normal
text, which is the honest reason to reach for it: a guaranteed
linear bound, not a faster average. The search reports every start
position where the pattern occurs, overlaps included, since the
same border logic that avoids re-reading also lets a match begin
inside the previous one, and by the same convention the language's
own count uses, the empty pattern is taken to occur at every
position including the end.
"""

from __future__ import annotations


def prefix_function(pattern: str) -> list[int]:
    table = [0] * len(pattern)
    border = 0
    for i in range(1, len(pattern)):
        while border > 0 and pattern[i] != pattern[border]:
            border = table[border - 1]
        if pattern[i] == pattern[border]:
            border += 1
        table[i] = border
    return table


def search(text: str, pattern: str) -> list[int]:
    if pattern == "":
        return list(range(len(text) + 1))
    table = prefix_function(pattern)
    matches = []
    matched = 0
    for i, char in enumerate(text):
        while matched > 0 and char != pattern[matched]:
            matched = table[matched - 1]
        if char == pattern[matched]:
            matched += 1
        if matched == len(pattern):
            matches.append(i - matched + 1)
            matched = table[matched - 1]
    return matches


def first(text: str, pattern: str) -> int:
    matches = search(text, pattern)
    return matches[0] if matches else -1


def contains(text: str, pattern: str) -> bool:
    return bool(search(text, pattern))


def count(text: str, pattern: str) -> int:
    return len(search(text, pattern))
