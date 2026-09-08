"""The health glass: every examiner's page on one desk, no verdict paraphrased.

A document is never sick in one place at a time, so the
health glass gathers the examiners that already exist, the
fabric census for structure, the attribution census for
voices, the prose numbers for the writing, and the
paragraph outline for shape, and lays their pages side by
side in their own words, because paraphrase is where
precision goes to die and a reader flipping between four
reports misses the correlation that is the actual
diagnosis. The glass adds exactly one number of its own,
the count of sections that had something to say, and its
closing line scales with that honestly rather than
grading: a quiet document is told it reads clean, a busy
one has its sections counted, and neither is scored,
because a document's health is a conversation and a grade
is a conversation ender. Each section keeps its examiner's
voice untouched, the glass being a desk and not an editor.
"""

from __future__ import annotations

from loom.attribution import page as attribution_page
from loom.census import page as census_page
from loom.paragraphs import outline
from loom.prose import page as prose_page
from loom.weave import Weave


def health(weave: Weave) -> str:
    sections = [
        ("structure", census_page(weave)),
        ("voices", attribution_page(weave)),
        ("writing", prose_page(weave)),
        ("shape", outline(weave)),
    ]
    body = []
    for name, page in sections:
        indented = page.replace("\n", "\n  ")
        body.append(f"{name}:\n  {indented}")

    if weave.visible_count() == 0:
        closing = (
            "an empty page; every examiner reports "
            "zero and every future is open"
        )
    else:
        closing = (
            f"{len(sections)} examiner(s) reported; "
            "no grade, because a document's health "
            "is a conversation and a grade is a "
            "conversation ender"
        )
    return "\n\n".join(
        [
            f"health of a "
            f"{weave.visible_count()}-glyph fabric:",
            *body,
            closing,
        ]
    )
