"""Reading time: the how-long-to-read estimate every article now carries, honestly hedged.

An article's reading-time badge is word count divided by a
reading speed, and this computes it, but it is careful to
present it as the estimate it is rather than a fact. The
speed is an average, and silent reading of ordinary prose
sits somewhere around two hundred words a minute for many
readers and far from it for many others, faster for a skimmer,
slower for a careful reader or a dense technical text, so the
default is stated and adjustable and the output is phrased in
the round terms an estimate deserves, about three minutes, not
three point one four. A document under a minute's reading says
under a minute rather than a fractional figure that pretends
to a precision the method does not have, and an empty document
has nothing to read and says so. The one thing it does not do
is weight by word difficulty or sentence complexity, because
those adjustments dress a rough estimate in the costume of a
model, and a reader is better served by a plain word-count
figure they can mentally adjust than by a number that hides
its own roughness behind arithmetic. The speed guard refuses a
non-positive rate, since reading at zero words a minute takes
forever and dividing by it says as much in a less useful way.
"""

from __future__ import annotations

from loom.errors import Invalid
from loom.prose import word_count
from loom.weave import Weave

DEFAULT_WPM = 200


def reading_minutes(weave: Weave, wpm: int = DEFAULT_WPM) -> float:
    if wpm <= 0:
        raise Invalid("a reading speed must be positive")
    return word_count(weave) / wpm


def reading_time(weave: Weave, wpm: int = DEFAULT_WPM) -> str:
    words = word_count(weave)
    if words == 0:
        return "nothing to read"
    minutes = reading_minutes(weave, wpm)
    if minutes < 1:
        return "under a minute"
    return f"about {round(minutes)} min"
