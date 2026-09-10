"""Urlcodec: percent-encoding, making arbitrary text safe to carry inside a URL.

A URL may contain only a limited set of characters, so any text put
into one, a search term, a path segment, a parameter value, has to
be encoded first. Percent-encoding does it by leaving the safe
characters alone and replacing every other byte with a percent sign
and its two hexadecimal digits. The safe set is the unreserved
characters of the URL standard, the letters, the digits, and a few
punctuation marks that no part of URL syntax uses, and everything
else, spaces, punctuation, and any non-ASCII character, is encoded.
The one point worth being careful about is what a byte is here. A
character outside ASCII is first turned into its several bytes in
the standard text encoding, and each of those bytes is
percent-encoded on its own, so a single accented letter becomes two
or more percent groups rather than one; decoding reverses that,
collecting the raw bytes back and decoding them as text at the end,
not one character at a time. I had assumed encoding could work
character by character, emitting one percent group per character; it
cannot for anything beyond ASCII, because the byte, not the
character, is the unit the encoding operates on, and a version that
percent-encodes a character's code point directly produces something
a standard decoder cannot read back. So this encodes the text's
bytes and decodes back to bytes before turning them into text, which
is the difference between round-tripping every character and only
the plain ones. Decoding rejects a malformed percent group, one not
followed by two hexadecimal digits, rather than passing it through as
if it were literal, since silently accepting it would make the
decode disagree with every conforming decoder. The caller may name
extra characters as safe to leave unencoded, for when a delimiter
should be preserved rather than escaped.
"""

from __future__ import annotations

import string

from loom.errors import Invalid

_UNRESERVED = frozenset(string.ascii_letters + string.digits + "-._~")


def quote(text: str, safe: str = "") -> str:
    allowed = _UNRESERVED | set(safe)
    out = []
    for byte in text.encode("utf-8"):
        char = chr(byte)
        if char in allowed:
            out.append(char)
        else:
            out.append(f"%{byte:02X}")
    return "".join(out)


def unquote(text: str) -> str:
    raw = bytearray()
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char == "%":
            group = text[index + 1 : index + 3]
            if len(group) != 2:
                raise Invalid("a percent group needs two hex digits")
            try:
                raw.append(int(group, 16))
            except ValueError:
                raise Invalid(f"{group!r} is not a hex byte") from None
            index += 3
        else:
            raw.extend(char.encode("utf-8"))
            index += 1
    return raw.decode("utf-8")
