"""BWT: reorder a text so its repeats cluster, reversibly, without discarding a thing.

The Burrows-Wheeler transform rearranges the characters of a text
into a permutation that groups similar contexts together, so that
characters preceded by the same following text end up adjacent, and
a text with structure comes out full of runs of repeated
characters. It does not compress on its own, it makes no text
shorter, but those runs are exactly what run-length and
move-to-front coding then squeeze, which is why it sits in front of
a compressor rather than being one. The transform appends a unique
end marker smaller than any real character, considers every
rotation of the resulting string, sorts them, and reads off the
last character of each sorted rotation; that last column is the
transform. Sorting the rotations is the same work as sorting the
suffixes, so this builds the suffix array and reads the character
just before each sorted suffix, reusing that machinery rather than
sorting whole rotations. The property that makes it worth the
trouble, and the part that surprised me, is that this is perfectly
reversible from the last column alone, with no extra information
stored: I had assumed scrambling the characters this way must lose
the order and need a stored index to undo, but the last column plus
the knowledge that the first column is simply the sorted characters
is enough, because the marker pins down where the original ended
and a mapping between the two columns walks the text back out one
character at a time. That mapping rests on a quiet fact, that equal
characters keep the same relative order in the first column as they
have in the last, so the kth occurrence of a character in one
column is the kth in the other, which is what lets the walk never
lose its place. The end marker is assumed absent from the input so
it stays unique, and the inverse strips it back off, returning
exactly the text that went in.
"""

from __future__ import annotations

from collections import Counter

from loom.errors import Invalid
from loom.suffixarray import suffix_array

SENTINEL = "\x00"


def transform(text: str) -> str:
    if SENTINEL in text:
        raise Invalid("the text already contains the reserved end marker")
    marked = text + SENTINEL
    order = suffix_array(marked)
    return "".join(marked[index - 1] for index in order)


def inverse(encoded: str) -> str:
    length = len(encoded)
    if length == 0:
        raise Invalid("the transform of a real text is never empty")
    counts = Counter(encoded)
    start: dict = {}
    running = 0
    for char in sorted(counts):
        start[char] = running
        running += counts[char]
    seen: Counter = Counter()
    last_to_first = [0] * length
    for index, char in enumerate(encoded):
        last_to_first[index] = start[char] + seen[char]
        seen[char] += 1
    # The first column is the sorted characters, so its top row is the
    # unique end marker; walking the last-to-first map from there reads
    # the marker-led rotation out backward.
    row = 0
    recovered = []
    for _ in range(length):
        recovered.append(encoded[row])
        row = last_to_first[row]
    recovered.reverse()
    return "".join(recovered[1:])
