"""Rewrap: apply the reflow wrapping to the document as operations, not just as a view.

The reflow module wraps a paragraph to a column and hands
back the wrapped text; this takes that text and makes it the
document, so the wrapping is real and shared rather than a
rendering one editor sees. It does so through the patch
machinery, diffing the current text against the reflowed
target and minting operations only for the runs that changed,
which for a rewrap is usually just the whitespace at the wrap
points, a space becoming a newline here, a newline becoming a
space there. That is the quiet virtue of routing it through
the patch: rewrapping a paragraph to a slightly different
width does not reshear every word, it moves the handful of
break characters that actually move, so the words keep their
strands and a comment anchored inside a rewrapped paragraph
stays put. It converges across replicas for the same reason
the patch does, and it inherits reflow's one firm rule, that
a word longer than the column is never chopped to fit but
placed alone and allowed to overflow, because the wrapping
target reflow computes already honours it. The width is the
caller's, since the right column for a document is the
caller's to know, and a rewrap to the width the text already
fits mints nothing, the patch finding no runs to change.
"""

from __future__ import annotations

from loom.author import Author
from loom.patch import patch
from loom.reflow import reflow
from loom.weave import Op


def rewrap(author: Author, width: int) -> list[Op]:
    return patch(author, reflow(author.text(), width))
