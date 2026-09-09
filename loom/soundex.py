"""Soundex: encode a word by its sound, so names that sound alike share a code.

Soundex is the old phonetic algorithm that maps a word to a
letter and three digits so that words pronounced alike encode
alike, the trick behind sounds-like search over names. This is
the American Soundex with its rules intact: keep the first
letter, map the consonants to the six digit groups by where
the mouth makes them, drop the vowels, and collapse adjacent
letters that share a code, with the two subtleties that make it
correct rather than approximate. A vowel between two same-coded
consonants keeps them separate, so both count, while an H or a
W between them is transparent and lets them collapse as if
adjacent, which is why Ashcraft encodes with the s and c
merged. The code is padded or trimmed to exactly four
characters, the fixed width that lets codes be compared and
indexed. The honest limit is the one every phonetic code has
and it is loud: Soundex is lossy and English-centric, so
Robert and Rupert collapse to one code and many unrelated
names collide, which is the feature for fuzzy matching and the
flaw for precision, and a caller must treat a shared code as a
maybe, not a match. It is offered for the sounds-like pass
that narrows a search, with the edit-distance and did-you-mean
modules for the closeness a phonetic code cannot measure.
"""

from __future__ import annotations

CODES = {}
for _digit, _letters in (
    ("1", "BFPV"),
    ("2", "CGJKQSXZ"),
    ("3", "DT"),
    ("4", "L"),
    ("5", "MN"),
    ("6", "R"),
):
    for _letter in _letters:
        CODES[_letter] = _digit


def soundex(name: str) -> str:
    letters = [char for char in name.upper() if char.isalpha()]
    if not letters:
        return ""
    result = letters[0]
    previous = CODES.get(letters[0], "")
    for char in letters[1:]:
        code = CODES.get(char, "")
        if code:
            if code != previous:
                result += code
            previous = code
        elif char in "HW":
            continue
        else:
            previous = ""
        if len(result) >= 4:
            break
    return (result + "000")[:4]


def sounds_like(first: str, second: str) -> bool:
    return soundex(first) == soundex(second) and bool(soundex(first))
