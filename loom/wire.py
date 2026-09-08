"""The wire: operations as lines of text, dull as a treaty and as binding.

Replicas share nothing but what survives this module, so
the format optimizes for the two readers that matter, the
parser and the person debugging at midnight: one operation
per line, fields separated by pipes, a leading verb so the
eye can grep a transcript, and glyphs escaped just enough
that pipes, newlines, and backslashes cannot impersonate
structure. Inserts carry verb, id, origin or the head
marker, rank, and glyph; shears carry verb, id, and
target; nothing carries anything else, because every field
is a compatibility promise and promises compound. Parsing
refuses loudly with the line quoted, a Torn for anything
that fails its own grammar, and round-tripping is tested
as identity in both directions, since a wire format that
drifts from its parser is two formats sharing a name.
"""

from __future__ import annotations

from loom.errors import Torn
from loom.ids import OpId
from loom.weave import HEAD, Insert, Op, Shear

HEAD_MARK = "^"


def _escape(glyph: str) -> str:
    return (
        glyph.replace("\\", "\\\\")
        .replace("|", "\\p")
        .replace("\n", "\\n")
    )


def _unescape(text: str) -> str:
    out = []
    index = 0
    while index < len(text):
        char = text[index]
        if char != "\\":
            out.append(char)
            index += 1
            continue
        if index + 1 >= len(text):
            raise Torn(
                f"{text!r} ends mid-escape; the glyph "
                "was cut off in transit"
            )
        code = text[index + 1]
        if code == "\\":
            out.append("\\")
        elif code == "p":
            out.append("|")
        elif code == "n":
            out.append("\n")
        else:
            raise Torn(
                f"\\{code} is not an escape this wire "
                "knows"
            )
        index += 2
    return "".join(out)


def encode(op: Op) -> str:
    if isinstance(op, Insert):
        origin = (
            HEAD_MARK
            if op.origin is HEAD
            else op.origin.wire()
        )
        return (
            f"ins|{op.id.wire()}|{origin}|{op.rank}|"
            f"{_escape(op.glyph)}"
        )
    return f"shr|{op.id.wire()}|{op.target.wire()}"


def decode(line: str) -> Op:
    parts = line.split("|")
    verb = parts[0]
    if verb == "ins":
        if len(parts) != 5:
            raise Torn(
                f"{line!r} is not an insert; inserts "
                "carry five fields and promises "
                "compound"
            )
        _, id_text, origin_text, rank_text, glyph = (
            parts
        )
        origin = (
            HEAD
            if origin_text == HEAD_MARK
            else OpId.parse(origin_text)
        )
        try:
            rank = int(rank_text)
        except ValueError as wrong:
            raise Torn(
                f"{line!r} carries a rank that is not "
                "a number"
            ) from wrong
        return Insert(
            id=OpId.parse(id_text),
            origin=origin,
            glyph=_unescape(glyph),
            rank=rank,
        )
    if verb == "shr":
        if len(parts) != 3:
            raise Torn(
                f"{line!r} is not a shear; shears "
                "carry three fields"
            )
        return Shear(
            id=OpId.parse(parts[1]),
            target=OpId.parse(parts[2]),
        )
    raise Torn(
        f"{line!r} opens with {verb!r}; the verbs on "
        "this wire are ins and shr"
    )


def encode_many(ops: list[Op]) -> str:
    return "\n".join(encode(op) for op in ops)


def decode_many(text: str) -> list[Op]:
    if not text:
        return []
    return [
        decode(line) for line in text.split("\n")
    ]
