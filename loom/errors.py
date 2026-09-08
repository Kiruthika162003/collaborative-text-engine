"""The refusals: every way the loom declines, named and sentenced.

A collaborative engine has one cardinal promise, that every
replica ends at the same text, and its errors exist to
protect that promise rather than to apologize for it.
Invalid marks requests that were never coherent, the
insert at an anchor nobody minted, the site that names
itself with an empty string. Missing marks references to
things the fabric has not seen, which in a distributed
setting is often not an error but an arrival out of order,
and the type exists so callers can tell buffer-and-wait
from give-up. Diverged is the alarm bell: two replicas
that should read identically do not, and nothing in this
codebase catches it to continue, because a divergence
survived is a divergence institutionalized. Torn marks
bytes that fail their own arithmetic, and Stale marks
operations replayed from a past the fabric has already
woven past. Every message is a sentence with a subject,
in the house style: say what refused, say why, and never
make the caller guess which of the five doors slammed.
"""

from __future__ import annotations


class LoomError(Exception):
    """The base refusal; catch this to catch the loom's whole voice."""


class Invalid(LoomError):
    """The request never cohered; no ordering of arrivals would fix it."""


class Missing(LoomError):
    """A reference to something unseen; possibly an arrival out of order."""


class Diverged(LoomError):
    """Two replicas that must read identically do not; the alarm, not a log line."""


class Torn(LoomError):
    """Bytes that fail their own arithmetic; corruption, not disagreement."""


class Stale(LoomError):
    """An operation from a past the fabric has already woven past."""
