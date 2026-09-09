"""Word lengths: the distribution of word lengths, where prose gives only the average.

The prose module reports the average word length, one number
that hides its own shape: an average of five is a document of
all five-letter words or an even mix of two and eight, and
those read nothing alike. This gives the distribution instead,
the count of words at each length, from which the shape is
visible and the derived figures fall out: the median length,
which resists the long outlier a mean chases, and the mode,
the length the document uses most, which the average never
names. It counts words the way prose does, whitespace-split
tokens, and inherits that definition's one wrinkle, that a
word with a trailing comma counts the comma toward its length,
which is stated because a distribution that silently stripped
punctuation would disagree with the average it sits beside.
The histogram renders the distribution as bars a reader scans,
each length's row scaled to the busiest so the shape shows
whatever the counts are, and it is a rendering, changing
nothing. An empty document distributes nothing and says so,
without the zero-length row that a naive counter would emit
for the single empty token a split of blank text returns.
"""

from __future__ import annotations

from loom.prose import words_of
from loom.weave import Weave


def distribution(weave: Weave) -> dict[int, int]:
    dist: dict[int, int] = {}
    for word in words_of(weave):
        dist[len(word)] = dist.get(len(word), 0) + 1
    return dist


def median_length(weave: Weave) -> float:
    lengths = sorted(len(word) for word in words_of(weave))
    if not lengths:
        return 0.0
    middle = len(lengths) // 2
    if len(lengths) % 2 == 1:
        return float(lengths[middle])
    return (lengths[middle - 1] + lengths[middle]) / 2


def mode_length(weave: Weave) -> int:
    dist = distribution(weave)
    if not dist:
        return 0
    return max(dist, key=lambda length: (dist[length], length))


def histogram(weave: Weave) -> str:
    dist = distribution(weave)
    if not dist:
        return "no words to measure"
    busiest = max(dist.values())
    lines = []
    for length in sorted(dist):
        count = dist[length]
        bar = "#" * max(1, count * 20 // busiest)
        lines.append(f"{length:>2}: {bar} {count}")
    return "\n".join(lines)
