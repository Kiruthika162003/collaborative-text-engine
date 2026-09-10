"""Sampling: shuffle a list and sample a stream uniformly, both easy to get subtly wrong.

Two related tasks live here, a fair shuffle and a fair sample, and
both have a well-known correct method and a plausible-looking wrong
one. The shuffle is Fisher-Yates: walk the list from the last
position to the first, and swap each position with one chosen
uniformly from itself and the positions before it, so by the time
the walk finishes every arrangement is equally likely. I had
thought shuffling by giving each item a random key and sorting on
the keys was just as good; it is fair too, but it pays a sort's
cost where Fisher-Yates is a single linear pass, and Fisher-Yates
has a famous trap that looks fine and is not: drawing the swap
partner from the whole list each step instead of from the current
position and those before it. That version runs, looks random, and
is biased, producing some permutations more often than others, a
wrong subtle enough to survive casual testing, which is why the
range the random index is drawn from is the whole correctness of
the routine. The sample is reservoir sampling, which picks a fixed
number of items uniformly from a stream whose length is not known
ahead of time. I had assumed uniform sampling needed the count
first, to choose which indices to keep; it does not. Keep the first
few items, then for each later item at position i replace a
randomly chosen held item with it with probability the sample size
over i, and the algebra makes every item of the stream end equally
likely to be held, whatever the final length turns out to be. That
independence from the length is the whole point, it samples a
stream too large to store or even to count, in one pass keeping only
the sample. Both routines take a seed so the same input and seed
give the same result, which is what lets a shuffle or a sample be
tested for the distribution it actually produces rather than being
unrepeatable.
"""

from __future__ import annotations

import random

from loom.errors import Invalid


def shuffle(items: list, seed: int | None = None) -> list:
    result = list(items)
    rng = random.Random(seed)
    for position in range(len(result) - 1, 0, -1):
        swap = rng.randint(0, position)
        result[position], result[swap] = result[swap], result[position]
    return result


def reservoir(stream: object, size: int, seed: int | None = None) -> list:
    if size < 0:
        raise Invalid("the sample size cannot be negative")
    rng = random.Random(seed)
    held: list = []
    for index, item in enumerate(stream):
        if index < size:
            held.append(item)
        else:
            slot = rng.randint(0, index)
            if slot < size:
                held[slot] = item
    return held
