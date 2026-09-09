"""Readability panel: the three grade formulas together, with their agreement measured.

One readability grade is a guess; three built on different
signals, agreeing, are a guess worth some trust. This runs the
Flesch-Kincaid grade, which leans on syllables per word, the
Coleman-Liau index, which leans on letters per word, and the
SMOG grade, which leans on long words per sentence, and puts
their three numbers side by side. The consensus is their plain
average, and the spread is the distance between the highest and
lowest, and the spread is the number that matters: when the
three agree, the text is ordinary in every dimension they
measure and the consensus is a fair estimate, but when they
spread wide the text is unusual in exactly the dimension one
formula weighs and the others do not, a document of short
sentences full of long words, say, and the consensus averages
away the very thing worth noticing. So the panel reports the
spread plainly rather than hiding it inside the average, and it
keeps the honest disclaimer all three share: these grade the
lengths of words and sentences, not the difficulty of the
thought, and a clear hard idea and a muddled easy one can read
identically to every formula here. It is a reading, not a
verdict, and its most useful output is often not the number but
the disagreement, which points at what is unusual about a text
faster than reading it does.
"""

from __future__ import annotations

from loom.colemanliau import index as coleman_liau
from loom.prose import word_count
from loom.readability import flesch_kincaid_grade
from loom.smog import grade as smog_grade
from loom.weave import Weave


def grades(weave: Weave) -> dict[str, float]:
    return {
        "flesch-kincaid": flesch_kincaid_grade(weave),
        "coleman-liau": coleman_liau(weave),
        "smog": smog_grade(weave),
    }


def consensus(weave: Weave) -> float:
    values = list(grades(weave).values())
    return round(sum(values) / len(values), 1)


def spread(weave: Weave) -> float:
    values = list(grades(weave).values())
    return round(max(values) - min(values), 1)


def report(weave: Weave) -> str:
    if word_count(weave) == 0:
        return "no prose to grade"
    parts = ", ".join(
        f"{name} {value}" for name, value in grades(weave).items()
    )
    return "\n".join(
        [
            f"grades: {parts}",
            f"consensus {consensus(weave)}, spread {spread(weave)}",
            "a wide spread means the text is unusual in one "
            "dimension; all three grade length, not thought",
        ]
    )
