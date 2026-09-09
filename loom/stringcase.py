"""String case: convert an identifier between snake, camel, Pascal, kebab, and constant.

Identifiers wear five common cases and code moves between
them constantly, so this converts among them by first
splitting an identifier into its component words and then
rejoining in the target style. The splitting is the clever
half and it handles the boundaries all five cases use:
underscores, hyphens, and spaces, and the case transitions
inside a run, a lowercase or digit followed by an uppercase
starting a new word, and an uppercase followed by an
uppercase-then-lowercase, which is what lets HTTPServer split
into HTTP and Server rather than swallowing the S. With the
words in hand the joins are simple: snake and kebab lowercase
and join with their separator, constant uppercases and joins
with an underscore, camel lowercases the first word and
capitalizes the rest, and Pascal capitalizes all. Round trips
hold within a style, and crossing styles is lossless in the
words even when the separators change, which is the property
that lets a rename tool convert a whole file's identifiers
without mangling them. Detection reads the separators and the
leading case to name a style, a best guess that is right for
the unambiguous cases and honestly cannot distinguish a
single lowercase word, which is valid snake and valid camel
and valid kebab all at once, so it names that flat rather than
pick one and imply a structure the word does not have.
"""

from __future__ import annotations

import re

BOUNDARY = re.compile(
    r"[_\- ]+|(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])"
)


def words(identifier: str) -> list[str]:
    return [part.lower() for part in BOUNDARY.split(identifier) if part]


def to_snake(identifier: str) -> str:
    return "_".join(words(identifier))


def to_kebab(identifier: str) -> str:
    return "-".join(words(identifier))


def to_constant(identifier: str) -> str:
    return "_".join(word.upper() for word in words(identifier))


def to_camel(identifier: str) -> str:
    parts = words(identifier)
    if not parts:
        return ""
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def to_pascal(identifier: str) -> str:
    return "".join(word.capitalize() for word in words(identifier))


def detect(identifier: str) -> str:
    if not identifier:
        return "empty"
    if "-" in identifier:
        return "kebab"
    if "_" in identifier:
        return "constant" if identifier.isupper() else "snake"
    if identifier[:1].isupper():
        return "pascal"
    if any(char.isupper() for char in identifier):
        return "camel"
    return "flat"
