"""HTML page: wrap the rendered body in a minimal, valid document shell.

The htmlrender module produces the body's HTML; this puts it
inside a whole document, the doctype, the html and head and
body elements, and a title, so the output is a page a browser
opens rather than a fragment a page must embed. The title is
the one piece of judgement it makes: given none, it takes the
document's first heading, which is what a reader would call
the page, and falls back to Untitled only when there is no
heading to name it, rather than leaving the title empty or
guessing from the prose. The title is escaped, because a
heading with an ampersand or an angle bracket must not break
the head any more than body text may break the body, and the
same escape the renderer trusts for content guards the title
here. The shell is deliberately minimal, a title and nothing
more in the head, no stylesheet, no generator meta, no
character-set declaration beyond what the serving layer adds,
because a page module that baked in a house style would be
imposing decisions a caller should make, and the honest floor
is a document that is valid and self-describing, leaving the
dressing to whoever serves it. The body is exactly what the
renderer produced, unwrapped and unaltered, so the page is the
render plus a frame and nothing is done to the content on the
way out that was not done on the way in.
"""

from __future__ import annotations

import re

from loom.htmlescape import escape
from loom.htmlrender import render

FIRST_HEADING = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)


def title_of(text: str) -> str:
    match = FIRST_HEADING.search(text)
    return match.group(1).strip() if match is not None else "Untitled"


def page(text: str, title: str | None = None) -> str:
    heading = title if title is not None else title_of(text)
    head = f"<head><title>{escape(heading)}</title></head>"
    body = render(text)
    return (
        "<!doctype html>\n<html>\n"
        f"{head}\n<body>\n{body}\n</body>\n</html>"
    )
