"""Operation identity: a site, a counter, and a total order everyone shares.

Concurrent editing works only if every replica, shown the
same two operations, ranks them the same way without a
meeting, and the OpId is the whole mechanism: a site name
and a per-site counter, ordered by counter first and site
name second. Counter-first matters because it makes the
order respect causality wherever causality exists, an
operation minted after seeing counter 41 will carry 42 and
sort after it on every replica, while site-second is the
coin flip for true ties, arbitrary but identically
arbitrary everywhere, which is the only kind of arbitrary
a distributed system is allowed. Site names are validated
at the door, nonempty, lowercase, no separators that would
break the wire form, because an id that cannot round-trip
through its own rendering is a bug wearing a name tag. The
wire form is site colon counter, chosen boring on purpose;
identity is the one place cleverness costs convergence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering

from loom.errors import Invalid, Torn

SITE_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")


def check_site(site: str) -> str:
    if not SITE_PATTERN.match(site):
        raise Invalid(
            f"{site!r} is not a site name; lowercase, "
            "digits, hyphens, starting with a letter, "
            "because an id that cannot round-trip its "
            "own rendering is a bug wearing a name tag"
        )
    return site


@total_ordering
@dataclass(frozen=True)
class OpId:
    site: str
    counter: int

    def __post_init__(self) -> None:
        check_site(self.site)
        if self.counter < 1:
            raise Invalid(
                f"counter {self.counter} for site "
                f"{self.site}; counters start at one, "
                "and zero is the name of nothing"
            )

    def __lt__(self, other: OpId) -> bool:
        return (self.counter, self.site) < (
            other.counter,
            other.site,
        )

    def wire(self) -> str:
        return f"{self.site}:{self.counter}"

    @classmethod
    def parse(cls, text: str) -> OpId:
        site, sep, counter_text = text.partition(":")
        if not sep:
            raise Torn(
                f"{text!r} is not an op id; the wire "
                "form is site colon counter, boring on "
                "purpose"
            )
        try:
            counter = int(counter_text)
        except ValueError as wrong:
            raise Torn(
                f"{text!r} carries a counter that is "
                "not a number"
            ) from wrong
        return cls(site=site, counter=counter)


def mint_after(site: str, seen_top: int) -> OpId:
    """The next id a site may mint after observing counters up to seen_top."""
    check_site(site)
    if seen_top < 0:
        raise Invalid(
            "a site cannot have seen fewer than zero "
            "operations"
        )
    return OpId(site=site, counter=seen_top + 1)
