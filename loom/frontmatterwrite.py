"""Front matter write: set and remove metadata fields as operations, block created as needed.

The frontmatter module reads the metadata block; this writes
it. Setting a field has three cases and this handles each
without the caller thinking about them: a field that already
exists has its value replaced in place, a new field is added
as a line before the closing delimiter, and a document with no
front matter at all gets a fresh block prepended above its
body. Removing a field drops its line and leaves the rest of
the block, delimiters and all, so a document that carried
metadata still declares that it does even after a field goes.
The whole change is expressed as a patch against the rebuilt
text, so it reuses the diff that touches only what differs and
converges across replicas the way a patch does, which means
setting one field does not disturb the strands of the fields
beside it or the body below. The value is written as the
plain string it is, matching the flat, untyped metadata the
reader parses, so a round trip through write and read returns
what went in. Creating a block puts it where front matter
belongs, at the very top, because that position is the reader's
whole definition of front matter, and a block written anywhere
else would be metadata the reader would refuse to see.
"""

from __future__ import annotations

from loom.author import Author
from loom.frontmatter import DELIMITER, parse
from loom.patch import patch
from loom.weave import Op


def _rebuild_set(lines: list[str], close: int, key: str, value: str) -> list[str]:
    block = lines[1:close]
    replaced = False
    for index, line in enumerate(block):
        if ":" in line and line.split(":", 1)[0].strip() == key:
            block[index] = f"{key}: {value}"
            replaced = True
            break
    if not replaced:
        block.append(f"{key}: {value}")
    return [DELIMITER, *block, DELIMITER, *lines[close + 1 :]]


def set_field(author: Author, key: str, value: str) -> list[Op]:
    matter = parse(author.weave)
    lines = author.text().split("\n")
    if matter.present:
        close = matter.body_line - 1
        new_lines = _rebuild_set(lines, close, key, value)
    else:
        new_lines = [DELIMITER, f"{key}: {value}", DELIMITER, *lines]
    return patch(author, "\n".join(new_lines))


def remove_field(author: Author, key: str) -> list[Op]:
    matter = parse(author.weave)
    if not matter.present or key not in matter.fields:
        return []
    lines = author.text().split("\n")
    close = matter.body_line - 1
    block = [
        line
        for line in lines[1:close]
        if not (":" in line and line.split(":", 1)[0].strip() == key)
    ]
    new_lines = [DELIMITER, *block, DELIMITER, *lines[close + 1 :]]
    return patch(author, "\n".join(new_lines))
