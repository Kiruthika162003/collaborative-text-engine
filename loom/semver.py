"""Semver: parse semantic versions and compare them by the specification's rules.

Semantic versioning packs a lot of ordering into a short
string, and getting the comparison right is subtle enough to
deserve its own module. This parses the major-dot-minor-dot-
patch core, an optional prerelease after a hyphen, and optional
build metadata after a plus, and compares two versions by the
spec's precedence, which has three rules a naive string compare
gets wrong. First, the numeric core compares field by field as
numbers, so ten follows nine rather than preceding it
alphabetically. Second, a version with a prerelease is lower
than the same version without one, because one-point-oh alpha
comes before the one-point-oh release, the opposite of what a
longer string usually implies. Third, prerelease identifiers
compare piece by piece, numeric ones as numbers and always
below alphanumeric ones, and a version with more identifiers
outranks a prefix of it, all of which the spec lays out and a
hand-rolled compare fumbles. Build metadata is ignored in
comparison entirely, since the spec says two versions differing
only in build are the same precedence, so one-point-oh plus one
build equals one-point-oh plus another for ordering. A string
that does not match the grammar is refused rather than compared
loosely, because a malformed version silently ordered would put
a release in the wrong place in a sorted list, and sorting a
list of versions is the operation this exists to make correct.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cmp_to_key

from loom.errors import Invalid

SEMVER = re.compile(
    r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$"
)


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...]
    build: str


def parse(text: str) -> Version:
    match = SEMVER.match(text.strip())
    if match is None:
        raise Invalid(f"{text!r} is not a semantic version")
    prerelease = tuple(match.group(4).split(".")) if match.group(4) else ()
    return Version(
        major=int(match.group(1)),
        minor=int(match.group(2)),
        patch=int(match.group(3)),
        prerelease=prerelease,
        build=match.group(5) or "",
    )


def _sign(difference: int) -> int:
    return (difference > 0) - (difference < 0)


def _compare_identifier(left: str, right: str) -> int:
    left_num, right_num = left.isdigit(), right.isdigit()
    if left_num and right_num:
        return _sign(int(left) - int(right))
    if left_num:
        return -1
    if right_num:
        return 1
    return _sign((left > right) - (left < right))


def compare(left: str, right: str) -> int:
    first = parse(left)
    second = parse(right)
    for a, b in (
        (first.major, second.major),
        (first.minor, second.minor),
        (first.patch, second.patch),
    ):
        if a != b:
            return _sign(a - b)
    if not first.prerelease and second.prerelease:
        return 1
    if first.prerelease and not second.prerelease:
        return -1
    for a_id, b_id in zip(first.prerelease, second.prerelease, strict=False):
        outcome = _compare_identifier(a_id, b_id)
        if outcome != 0:
            return outcome
    return _sign(len(first.prerelease) - len(second.prerelease))


def sort_versions(versions: list[str]) -> list[str]:
    return sorted(versions, key=cmp_to_key(compare))
