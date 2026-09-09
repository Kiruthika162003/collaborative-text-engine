"""Strip markdown: reduce formatted text to the words underneath, for counting and reading.

A word count run on Markdown counts the stars and hashes as
if they were text, and a screen reader reads them aloud, so
there is a real need to see the prose with its formatting
removed. This does that, taking the heading hashes off the
front of a line, the blockquote and list markers too, the
emphasis stars and underscores from around a phrase, the
backticks from inline code, and the link syntax down to its
label, which is the part a reader reads. Fenced code blocks
are kept as their literal content with the fence lines
dropped, because the code is text a reader wants and the
fences are not. The honest framing is that this is a
de-formatter built from regular expressions, not a Markdown
parser, and it says so: it handles the common shapes a
writing room types and can be fooled by the exotic, a literal
asterisk a writer meant as a multiplication sign, a nested
emphasis three deep, a link with balanced parentheses in its
url. Those edge cases are where a real parser earns its
weight, and this does not pretend to be one; it is the fast,
good-enough pass that makes a word count honest and a read-
aloud legible, and knowing its limits is part of using it
rather than a flaw hidden behind a confident output.
"""

from __future__ import annotations

import re

FENCE = re.compile(r"^`{3,}")
HEADING = re.compile(r"^#{1,6}\s+")
QUOTE = re.compile(r"^\s*>\s?")
LIST_MARKER = re.compile(r"^(\s*)(?:[-*+]|\d+\.)\s+")
IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
BOLD_STAR = re.compile(r"\*\*([^*]+)\*\*")
BOLD_UNDER = re.compile(r"__([^_]+)__")
ITALIC_STAR = re.compile(r"\*([^*]+)\*")
ITALIC_UNDER = re.compile(r"_([^_]+)_")
CODE = re.compile(r"`([^`]+)`")


def _strip_block(line: str) -> str:
    line = HEADING.sub("", line)
    line = QUOTE.sub("", line)
    return LIST_MARKER.sub(r"\1", line)


def _strip_inline(line: str) -> str:
    line = IMAGE.sub(r"\1", line)
    line = LINK.sub(r"\1", line)
    line = BOLD_STAR.sub(r"\1", line)
    line = BOLD_UNDER.sub(r"\1", line)
    line = ITALIC_STAR.sub(r"\1", line)
    line = ITALIC_UNDER.sub(r"\1", line)
    return CODE.sub(r"\1", line)


def plain(text: str) -> str:
    out = []
    in_fence = False
    for line in text.split("\n"):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            out.append(line)
            continue
        out.append(_strip_inline(_strip_block(line)))
    return "\n".join(out)


def plain_words(text: str) -> int:
    return len(plain(text).split())
