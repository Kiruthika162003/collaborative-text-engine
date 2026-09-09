"""Completion: finish a word from the document's own vocabulary, not a dictionary.

Autocomplete in a shared document draws from the words the
room has already written, which is exactly right for the job
it does: it steers collaborators toward the terms already in
use, so a document that says repository once keeps saying
repository rather than sprouting a repo and a repos beside
it. Given a prefix it returns the words that start with it,
folded so The and the count as one word and the more common
surface form is the one offered, ranked by how often each
appears so the term the document actually favours rises to
the top, ties broken alphabetically for a stable order. The
scope is the honest limit and the honest feature at once:
it will never suggest a word nobody has typed, so it cannot
finish a term the writer is introducing for the first time,
and that is the trade a document-vocabulary completer makes
on purpose, consistency over coverage, because a dictionary
completer that offered every English word would bury the
document's own vocabulary under the language's. The prefix
itself is not offered back, since completing a word to
itself is not a completion, and an empty prefix is refused
because it matches every word and a suggestion list of
everything is a suggestion of nothing.
"""

from __future__ import annotations

import re

from loom.errors import Invalid
from loom.weave import Weave

WORD = re.compile(r"[A-Za-z0-9]+")


def _folded(weave: Weave) -> dict[str, dict[str, int]]:
    surfaces: dict[str, dict[str, int]] = {}
    for word in WORD.findall(weave.text()):
        forms = surfaces.setdefault(word.lower(), {})
        forms[word] = forms.get(word, 0) + 1
    return surfaces


def _surface(forms: dict[str, int]) -> str:
    return max(forms, key=lambda form: (forms[form], form))


def ranked(weave: Weave, prefix: str) -> list[tuple[str, int]]:
    if not prefix:
        raise Invalid(
            "an empty prefix matches every word; completion "
            "needs something to finish"
        )
    low = prefix.lower()
    candidates = []
    for key, forms in _folded(weave).items():
        if key.startswith(low) and key != low:
            candidates.append((_surface(forms), sum(forms.values())))
    candidates.sort(key=lambda pair: (-pair[1], pair[0]))
    return candidates


def complete(weave: Weave, prefix: str, limit: int = 5) -> list[str]:
    return [surface for surface, _count in ranked(weave, prefix)[:limit]]


def vocabulary_size(weave: Weave) -> int:
    return len(_folded(weave))
