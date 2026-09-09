"""Coleman-Liau: a readability grade from letters and sentences, no syllables counted.

The readability module computes Flesch's index, which rests on
a syllable count that no heuristic gets fully right; the
Coleman-Liau index is the answer to that, a grade-level formula
built from two counts a machine gets exactly, the average
letters per hundred words and the average sentences per hundred
words. It trades one blindness for another honestly: where
Flesch can misjudge because its syllable count is a guess, this
cannot see how a word sounds at all, so a document of long
words that happen to be easy to say scores harder than it
reads. Neither is truth; each is arithmetic on lengths, and
having both lets a caller see when they agree, which is when
the grade estimate is worth trusting, and when they diverge,
which is a sign the text is unusual in exactly the dimension
the two formulas measure differently. The letters come from
the character-stats module, the sentences from the same
counter the other readability tools use, and the words from
prose, so all three agree with the rest of the engine rather
than each counting its own way. An empty document has no grade
and returns zero without pretending to measure prose that is
not there, and the grade is a formula output that can go
negative or past any real grade for degenerate text, reported
as the number the formula gives rather than clamped into a
plausible range, because clamping would hide the degeneracy a
caller wants to see.
"""

from __future__ import annotations

from loom.charstats import counts
from loom.prose import word_count
from loom.readability import sentence_count
from loom.weave import Weave


def index(weave: Weave) -> float:
    words = word_count(weave)
    if words == 0:
        return 0.0
    letters = counts(weave.text())["letters"]
    sentences = sentence_count(weave)
    letters_per_100 = letters / words * 100
    sentences_per_100 = sentences / words * 100
    grade = 0.0588 * letters_per_100 - 0.296 * sentences_per_100 - 15.8
    return round(grade, 1)


def report(weave: Weave) -> str:
    if word_count(weave) == 0:
        return "no prose to grade"
    return (
        f"Coleman-Liau grade {index(weave)}; letters and sentences, "
        "no syllables, so it cannot hear how a word sounds"
    )
