"""Proofread: the advisory checks gathered into one pass a writer runs before sharing.

A writer about to share a draft wants one glance that runs
the mechanical checks, and this gathers them: the doubled
words and duplicated lines the repeats module finds, the
acronyms the acronyms module never saw defined, and the
brackets the brackets module could not balance. It gathers
rather than re-judges, quoting each organ's count in the
organ's own terms, because every one of these checks already
states its own caveats, that had had is real English, that a
SHOUTED word looks like an acronym, that a smiley's
parenthesis reads as a bracket, and re-deciding them here
would either duplicate those caveats or, worse, drop them and
present a hedge as a verdict. So proofread is a collector, not
a corrector: it changes nothing, it makes no edits, it lists
what the checks noticed and leaves every call to the writer,
which is the only honest thing an automated proofreader can
be, since the ones that silently fix are the ones that
silently break. A clean pass says so plainly, and a pass with
findings orders them the way a writer triages, the outright
errors of unbalanced brackets and duplicated lines above the
judgement calls of doubled words and undefined acronyms,
because a broken bracket is almost always wrong and a doubled
word only usually is.
"""

from __future__ import annotations

from loom.acronyms import undefined
from loom.brackets import balance
from loom.repeats import doubled_words, duplicate_lines
from loom.weave import Weave


def findings(weave: Weave) -> list[str]:
    text = weave.text()
    items: list[str] = []
    if not balance(text).balanced:
        items.append("unbalanced brackets")
    dup_lines = duplicate_lines(weave)
    if dup_lines:
        items.append(f"{len(dup_lines)} duplicated line(s)")
    doubles = doubled_words(weave)
    if doubles:
        words = ", ".join(sorted({repeat.word.lower() for repeat in doubles}))
        items.append(f"{len(doubles)} doubled word(s): {words}")
    missing = undefined(weave)
    if missing:
        items.append("undefined acronym(s): " + ", ".join(missing))
    return items


def clean(weave: Weave) -> bool:
    return not findings(weave)


def report(weave: Weave) -> str:
    found = findings(weave)
    if not found:
        return "proofread clean; nothing the mechanical checks caught"
    return "\n".join(
        [
            f"proofread found {len(found)} thing(s) to look at:",
            *(f"  - {item}" for item in found),
            "a collector, not a corrector; every call is the writer's",
        ]
    )
