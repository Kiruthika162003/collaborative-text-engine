"""Heading titles: apply title case to every heading in a document, as operations.

The title-case module capitalizes one heading; this applies it
to all of them in a single pass, so a document with a dozen
sentence-case headings gets a consistent title-cased outline
without the writer retitling each by hand. It rebuilds the text
with each heading's title run through the title-case rules and
the hash markers left alone, and applies the change as a patch,
so only the letters that actually change case are touched and a
heading already in title case keeps its strands. Because title
case is idempotent, running this twice changes nothing the
second time, which makes it safe on every save; because it
patches, it converges across replicas like every other
text-editing pass here. It touches only heading lines, the ones
that open with hash marks, so a sentence in the body that
happens to look like a title is left as prose, and it inherits
the title-case module's small-word rules and its one stated
whitespace effect, that the title's internal spacing is
normalized to single spaces, which is right for a heading and
named so a caller is not surprised. It changes the case and
nothing else about the headings; it does not renumber them or
add anchors, because those are other passes with other names,
and a tool that quietly did all three would surprise a caller
who asked only for consistent capitalization.
"""

from __future__ import annotations

import re

from loom.author import Author
from loom.linewise import lines_of
from loom.patch import patch
from loom.titlecase import title_case
from loom.weave import Op

HEADING = re.compile(r"^(#{1,6}\s+)(.*)$")


def titlecase_headings(author: Author) -> list[Op]:
    rebuilt = []
    for line in lines_of(author.weave):
        match = HEADING.match(line)
        if match is not None:
            rebuilt.append(match.group(1) + title_case(match.group(2)))
        else:
            rebuilt.append(line)
    return patch(author, "\n".join(rebuilt))
