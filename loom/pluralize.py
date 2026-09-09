"""Pluralize: turn a singular noun into its plural by English's rules and exceptions.

Pluralizing an English noun is mostly rules with a stubborn
list of exceptions, and this handles both: a table of
irregulars that no rule produces, child to children and person
to people, a set of words that do not change, sheep and fish,
and then the regular rules, y after a consonant becoming ies,
a sibilant ending taking es, an f or fe often becoming ves, and
everything else taking a plain s. It is upfront that this is
rule-based and not a dictionary, so it gets the common cases
and misses the ones English keeps to spite rules: it will make
cactus into cactuses where a Latinist wants cacti, and roof
into rooves where the right answer is roofs, because the f-to-
ves rule is a tendency, not a law. Those are named rather than
hidden, and a caller with a domain full of such words extends
the irregulars table rather than trusting the rules blindly.
The case of the input is carried to the output, so Child
pluralizes to Children and CHILD toward CHILDREN, since a
plural that dropped the capital of a proper start would look
wrong in a sentence. The count-noun helper is the common reason
to pluralize at all, choosing singular or plural by a number so
one cat and two cats and zero cats each read right, with zero
taking the plural the way English does, zero cats, not zero
cat.
"""

from __future__ import annotations

import re

IRREGULAR = {
    "child": "children",
    "person": "people",
    "man": "men",
    "woman": "women",
    "mouse": "mice",
    "foot": "feet",
    "tooth": "teeth",
    "goose": "geese",
    "ox": "oxen",
}
UNCHANGED = frozenset(
    {"sheep", "fish", "deer", "series", "species", "aircraft"}
)


def _carry_case(source: str, plural: str) -> str:
    if source.isupper():
        return plural.upper()
    if source[:1].isupper():
        return plural.capitalize()
    return plural


def pluralize(word: str) -> str:
    low = word.lower()
    if low in UNCHANGED:
        return word
    if low in IRREGULAR:
        return _carry_case(word, IRREGULAR[low])
    if re.search(r"[^aeiou]y$", low):
        plural = word[:-1] + "ies"
    elif re.search(r"(s|sh|ch|x|z)$", low):
        plural = word + "es"
    elif low.endswith("fe"):
        plural = word[:-2] + "ves"
    elif low.endswith("f"):
        plural = word[:-1] + "ves"
    else:
        plural = word + "s"
    return plural


def count_noun(count: int, singular: str) -> str:
    noun = singular if count == 1 else pluralize(singular)
    return f"{count} {noun}"
