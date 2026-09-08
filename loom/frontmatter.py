"""Front matter: the metadata block at the very top, read only where it belongs.

Many documents open with a fenced block of key-value
metadata, title, author, date, delimited by a line of three
dashes above and below, and this reads it, but only from the
very top, because that position is the whole definition. A
line of three dashes in the middle of a document is a
thematic break, a horizontal rule, and reading it as front
matter would tear metadata out of the prose; front matter is
front matter only when the first line of the document opens
it. The block is closed by the next line of three dashes,
and an opening with no closing is not front matter at all,
reported absent and flagged, because guessing where an
unclosed block ends would swallow an arbitrary run of the
document's real text into a metadata dictionary nobody wrote.
Each line inside is a key and a value split on the first
colon, both trimmed, and a line without a colon is kept
aside as malformed rather than dropped or guessed into a
key, so a writer who fat-fingered a field sees it named
rather than silently lost. The simplifications are declared:
values are raw strings, not typed, and there are no nested
structures or lists, because the metadata a writing room
actually uses is flat, and a full parser would be a
dependency the feature does not need.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.weave import Weave

DELIMITER = "---"


@dataclass(frozen=True)
class Frontmatter:
    present: bool
    fields: dict[str, str] = field(default_factory=dict)
    malformed: list[str] = field(default_factory=list)
    body_line: int = 0


def parse(weave: Weave) -> Frontmatter:
    lines = weave.text().split("\n")
    if not lines or lines[0].strip() != DELIMITER:
        return Frontmatter(present=False)
    close = None
    for index in range(1, len(lines)):
        if lines[index].strip() == DELIMITER:
            close = index
            break
    if close is None:
        return Frontmatter(present=False)
    fields: dict[str, str] = {}
    malformed: list[str] = []
    for line in lines[1:close]:
        if not line.strip():
            continue
        if ":" not in line:
            malformed.append(line.strip())
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return Frontmatter(
        present=True,
        fields=fields,
        malformed=malformed,
        body_line=close + 1,
    )


def get(weave: Weave, key: str, default: str = "") -> str:
    return parse(weave).fields.get(key, default)


def body(weave: Weave) -> str:
    matter = parse(weave)
    if not matter.present:
        return weave.text()
    lines = weave.text().split("\n")
    return "\n".join(lines[matter.body_line :])


def report(weave: Weave) -> str:
    matter = parse(weave)
    if not matter.present:
        return "no front matter; the document starts with its body"
    lines = [f"{len(matter.fields)} field(s):"]
    for key in sorted(matter.fields):
        lines.append(f"  {key}: {matter.fields[key]}")
    if matter.malformed:
        lines.append(
            f"  {len(matter.malformed)} malformed line(s) kept aside"
        )
    return "\n".join(lines)
