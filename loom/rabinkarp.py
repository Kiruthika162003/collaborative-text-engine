"""Rabin-Karp: find a pattern by hashing a sliding window and rolling the hash along.

Rabin-Karp turns substring search into number comparison. It
hashes the pattern once, then slides a window of the pattern's
length across the text and hashes what the window covers, and
wherever the window's hash equals the pattern's hash it has found
a candidate. The trick that makes it worth doing is the roll: the
hash of the next window is computed from the current one in a
fixed number of steps, by subtracting the character sliding out of
the front, shifting the rest up one place in the chosen base, and
adding the character sliding in at the back, so the window's hash
is maintained in constant work per step rather than rehashing the
whole window each time. That makes one pass across the text, each
step a little arithmetic, linear in the text on the average. The
hash is taken modulo a large prime so the numbers stay bounded,
and that modulo is exactly where the care is needed. I had guessed
collisions would be rare enough to trust the hash and skip
checking the actual characters; on random text they are genuinely
rare, but rare is not never, and a single collision reports a match
where the strings differ, so the character check on a hash hit is
not an optimization to drop but the thing that keeps the answer
correct. With the check in place the worst case is back to
quadratic, when an adversarial text makes many windows share the
pattern's hash and every one has to be verified in full, which is
why Rabin-Karp is reached for its simplicity and for how naturally
it extends to hunting many patterns at once by hashing them all,
not for a guaranteed linear bound the way the prefix-table search
gives one. It reports every start position including overlaps, and
the empty pattern is taken to occur at every position by the same
convention the other searches here use.
"""

from __future__ import annotations

BASE = 257
MOD = 1_000_000_007


def rolling_hash(text: str) -> int:
    value = 0
    for char in text:
        value = (value * BASE + ord(char)) % MOD
    return value


def search(text: str, pattern: str) -> list[int]:
    text_length = len(text)
    pattern_length = len(pattern)
    if pattern == "":
        return list(range(text_length + 1))
    if pattern_length > text_length:
        return []
    lead = pow(BASE, pattern_length - 1, MOD)
    pattern_hash = rolling_hash(pattern)
    window_hash = rolling_hash(text[:pattern_length])
    matches = []
    for start in range(text_length - pattern_length + 1):
        if window_hash == pattern_hash and text[start : start + pattern_length] == pattern:
            matches.append(start)
        if start < text_length - pattern_length:
            leaving = ord(text[start]) * lead
            entering = ord(text[start + pattern_length])
            window_hash = ((window_hash - leaving) * BASE + entering) % MOD
    return matches


def first(text: str, pattern: str) -> int:
    matches = search(text, pattern)
    return matches[0] if matches else -1


def contains(text: str, pattern: str) -> bool:
    return bool(search(text, pattern))
