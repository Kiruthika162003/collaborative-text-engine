"""Number words: spell an integer in English and read the spelling back to the integer.

Numbers appear in prose as words as often as digits, and this
converts between the two over the range zero to nine hundred
ninety-nine thousand nine hundred ninety-nine. Spelling builds
the phrase the way the language does, a hundreds part and a
tens-and-ones part per thousand group, hyphenating the
compound tens like forty-two the way a style guide asks and
joining the groups with the scale word thousand. Reading is
the inverse and it round-trips: the words this spells parse
back to the number it started from, which is the property
worth having, because a speller and a parser that disagree
are two half-features. The reader accumulates a running group
and folds it in at each scale word, so one thousand two
hundred thirty-four reassembles in the order it was written,
and it rejects a word it does not know rather than skipping
it, since a silent skip would read three cats as three. The
conventions are American and stated: no and between hundred
and the tens, the way the phrase is written in the United
States, and hyphens in the compound tens; a document following
British phrasing with its ands would need those tolerated,
which is a deliberate omission rather than an oversight, kept
out because guessing which ands are conjunctions and which are
number glue is a harder problem than the feature needs.
"""

from __future__ import annotations

import re

from loom.errors import Invalid

ONES = [
    "zero", "one", "two", "three", "four", "five", "six", "seven",
    "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
    "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",
]
TENS = {
    2: "twenty", 3: "thirty", 4: "forty", 5: "fifty",
    6: "sixty", 7: "seventy", 8: "eighty", 9: "ninety",
}

WORDS = {word: value for value, word in enumerate(ONES)}
WORDS.update({word: tens * 10 for tens, word in TENS.items()})
WORDS["hundred"] = 100
WORDS["thousand"] = 1000


def _under_hundred(number: int) -> str:
    if number < 20:
        return ONES[number]
    tens, ones = divmod(number, 10)
    return TENS[tens] + (f"-{ONES[ones]}" if ones else "")


def _under_thousand(number: int) -> str:
    hundreds, rest = divmod(number, 100)
    parts = []
    if hundreds:
        parts.append(f"{ONES[hundreds]} hundred")
    if rest:
        parts.append(_under_hundred(rest))
    return " ".join(parts)


def spell(number: int) -> str:
    if not 0 <= number <= 999999:
        raise Invalid(
            f"{number} is outside 0..999999; this speller stops there"
        )
    if number == 0:
        return "zero"
    thousands, rest = divmod(number, 1000)
    parts = []
    if thousands:
        parts.append(f"{_under_thousand(thousands)} thousand")
    if rest:
        parts.append(_under_thousand(rest))
    return " ".join(parts)


def parse_words(text: str) -> int:
    tokens = [token for token in re.split(r"[\s-]+", text.strip().lower()) if token]
    if not tokens:
        raise Invalid("no words to read as a number")
    total = 0
    current = 0
    for token in tokens:
        if token not in WORDS:
            raise Invalid(f"{token!r} is not a number word")
        value = WORDS[token]
        if value == 100:
            current *= 100
        elif value == 1000:
            total += current * 1000
            current = 0
        else:
            current += value
    return total + current
