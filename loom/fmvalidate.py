"""Front matter validate: check the metadata block against required fields and simple types.

A document's front matter often has a contract, a set of
fields that must be present and a shape each should take, and
this checks a block against one: which required fields are
missing, and which present fields hold a value that does not
match the type expected of them. The type checks are
deliberately lightweight, an integer is a run of digits with
an optional sign, a boolean is one of the words a human writes
for yes or no, and a date is the ISO year-month-day, because
front matter is flat strings and a heavyweight type system
over strings would be more machinery than the block earns. A
type this does not know is not validated rather than guessed
at, so a caller can require a field's presence without also
constraining its shape, and an unknown type name passes
silently rather than failing every value against a check that
does not exist. It reports problems and coerces nothing, in
the reading-organ tradition: a field that should be an integer
and holds a word is named as wrong and left as it is, because
turning it into a zero would hide the mistake the author wants
to see. A block that satisfies its contract yields an empty
problem list, which is the clean signal a caller gates on, and
a document with no front matter fails every required field,
since a missing block is a missing everything, not a pass by
absence.
"""

from __future__ import annotations

import re

from loom.frontmatter import parse
from loom.weave import Weave

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BOOLEANS = frozenset({"true", "false", "yes", "no"})


def _matches(value: str, kind: str) -> bool:
    if kind == "int":
        return value.lstrip("-").isdigit()
    if kind == "bool":
        return value.lower() in BOOLEANS
    if kind == "date":
        return ISO_DATE.match(value) is not None
    return True


def validate(
    weave: Weave,
    required: frozenset[str] = frozenset(),
    types: dict[str, str] | None = None,
) -> list[str]:
    types = types or {}
    matter = parse(weave)
    problems = []
    for field in sorted(required):
        if field not in matter.fields:
            problems.append(f"missing required field {field!r}")
    for field, kind in sorted(types.items()):
        if field in matter.fields and not _matches(matter.fields[field], kind):
            problems.append(
                f"{field!r} is not a {kind}: {matter.fields[field]!r}"
            )
    return problems


def is_valid(
    weave: Weave,
    required: frozenset[str] = frozenset(),
    types: dict[str, str] | None = None,
) -> bool:
    return not validate(weave, required, types)
