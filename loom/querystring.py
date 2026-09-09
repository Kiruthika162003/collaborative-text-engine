"""Query string: parse and build URL query strings with percent-encoding.

A URL query string is key-value pairs joined by ampersands with
the unsafe characters percent-encoded, and this reads and
writes it in the form-encoded style, the one HTML forms and
most APIs use. Percent-encoding is the core: a character
outside the unreserved set, the letters, digits, and a few
punctuation marks safe everywhere, is written as a percent sign
and its bytes in hex, and a space is written as a plus, the
form convention; decoding reverses both, turning a plus back
into a space and a percent-hex pair back into its byte, then
reading the bytes as UTF-8 so an encoded non-ASCII character
returns whole. A key can appear more than once, which is how a
query carries a list, so parsing collects each key's values
into a list rather than letting a later value overwrite an
earlier, which would silently drop data a caller sent on
purpose. Building takes a value or a list per key and emits a
pair for each, so the list a parse produced encodes back to the
repeated key it came from, and the round trip holds through the
encoding: a set of parameters built into a string and parsed
back returns the same keys and values. Everything is a string,
because a query carries text and typing it would be a guess; a
caller reads the strings and coerces knowing what a field
means. Order within a key is preserved, since the position of
repeated values sometimes matters and reordering them would
change a query the caller composed deliberately.
"""

from __future__ import annotations

import string

UNRESERVED = frozenset(string.ascii_letters + string.digits + "-._~")


def quote(text: str) -> str:
    out = []
    for char in text:
        if char in UNRESERVED:
            out.append(char)
        elif char == " ":
            out.append("+")
        else:
            out.extend(f"%{byte:02X}" for byte in char.encode("utf-8"))
    return "".join(out)


def unquote(text: str) -> str:
    out = bytearray()
    index = 0
    while index < len(text):
        char = text[index]
        if char == "%" and index + 3 <= len(text):
            out.append(int(text[index + 1 : index + 3], 16))
            index += 3
        elif char == "+":
            out.append(0x20)
            index += 1
        else:
            out.extend(char.encode("utf-8"))
            index += 1
    return out.decode("utf-8")


def parse(query: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    if not query:
        return result
    for pair in query.split("&"):
        if not pair:
            continue
        key, _, value = pair.partition("=")
        result.setdefault(unquote(key), []).append(unquote(value))
    return result


def encode(params: dict[str, str | list[str]]) -> str:
    parts = []
    for key, value in params.items():
        values = value if isinstance(value, list) else [value]
        for item in values:
            parts.append(f"{quote(key)}={quote(str(item))}")
    return "&".join(parts)
