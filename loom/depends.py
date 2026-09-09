"""Depends: the causal dependencies of an operation, the readiness rule stated plainly.

The mailroom buffers operations until they are safe to weave;
this is the pure rule underneath that buffering, the set of
operations any given one depends on, computed and named so the
causal model is a thing a reader can inspect rather than infer
from the buffering code. An operation depends on two kinds of
predecessor. The first is contiguity: an operation is the nth
from its site, and the site's law is that its operations
deliver in order, so any operation past the first depends on
its own site's immediately preceding one, the id with the
counter one lower. The second is structure: an insert cannot
weave until the strand it was typed after exists, so it
depends on its origin unless that origin is the head, which is
always present; a shear cannot weave until the strand it
removes exists, so it depends on its target. An operation
whose dependencies are all delivered is ready, and the ones
not yet delivered are exactly what a buffer is waiting for, so
this answers both the yes-or-no and the what-for that a
buffer needs. It computes dependencies from the operation
alone, holding no state, which is why it can be tested against
hand-built delivery sets and why the mailroom can trust it:
the rule is the same whether asked here or enforced there.
"""

from __future__ import annotations

from loom.ids import OpId
from loom.weave import HEAD, Insert, Op


def dependencies(op: Op) -> set[OpId]:
    deps: set[OpId] = set()
    if op.id.counter > 1:
        deps.add(OpId(site=op.id.site, counter=op.id.counter - 1))
    if isinstance(op, Insert):
        if op.origin is not HEAD:
            deps.add(op.origin)
    else:
        deps.add(op.target)
    return deps


def ready(op: Op, delivered: set[OpId]) -> bool:
    return dependencies(op) <= delivered


def missing(op: Op, delivered: set[OpId]) -> set[OpId]:
    return dependencies(op) - delivered
