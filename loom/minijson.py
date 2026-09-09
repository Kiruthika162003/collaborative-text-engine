"""Mini JSON: encode Python values to JSON and parse JSON back, built from scratch.

This is a small JSON reader and writer written without the
standard library's, because an engine whose subject is text and
structure benefits from owning a format it can read in full
rather than treating as a black box. Encoding walks a value and
emits the JSON for it: null, true, false, numbers as
themselves, strings escaped so quotes and control characters
cannot break the structure, arrays and objects recursively.
Decoding is a recursive-descent parser with a cursor, the
textbook shape, that reads a value and refuses trailing content
so a document that is a valid value followed by garbage is
rejected rather than silently accepting the prefix. The round
trip holds for the types JSON has: encode a value and parse it
back and the value returns, which is the property that lets a
caller store structured data as text and read it whole. The
scope is stated. Numbers come back as an int when they have no
fractional or exponent part and a float otherwise, the natural
Python mapping. Duplicate keys in an object resolve to the last,
the common convention. The exotic corners JSON's grammar allows
but few producers emit, and the non-standard NaN and Infinity
some emit but the grammar forbids, are out of scope, and a
malformed document is refused with the position named rather
than half-parsed, because a parser that guesses past a syntax
error turns a data-corruption bug into a silent wrong answer.
"""

from __future__ import annotations

from loom.errors import Invalid, Torn

_ESCAPES = {
    '"': '\\"',
    "\\": "\\\\",
    "\n": "\\n",
    "\t": "\\t",
    "\r": "\\r",
    "\b": "\\b",
    "\f": "\\f",
}
_UNESCAPE = {
    '"': '"',
    "\\": "\\",
    "/": "/",
    "n": "\n",
    "t": "\t",
    "r": "\r",
    "b": "\b",
    "f": "\f",
}


def _encode_str(text: str) -> str:
    out = ['"']
    for char in text:
        if char in _ESCAPES:
            out.append(_ESCAPES[char])
        elif ord(char) < 0x20:
            out.append(f"\\u{ord(char):04x}")
        else:
            out.append(char)
    out.append('"')
    return "".join(out)


def encode(value: object) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return _encode_str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, list):
        return "[" + ",".join(encode(item) for item in value) + "]"
    if isinstance(value, dict):
        pairs = (
            _encode_str(str(key)) + ":" + encode(val)
            for key, val in value.items()
        )
        return "{" + ",".join(pairs) + "}"
    raise Invalid(f"cannot encode {type(value).__name__} as JSON")


class _Parser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def _skip(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos] in " \t\n\r":
            self.pos += 1

    def _fail(self, message: str) -> Torn:
        return Torn(f"{message} at position {self.pos}")

    def value(self) -> object:
        self._skip()
        if self.pos >= len(self.text):
            raise self._fail("unexpected end of input")
        char = self.text[self.pos]
        if char == '"':
            return self._string()
        if char == "{":
            return self._object()
        if char == "[":
            return self._array()
        if self.text.startswith("true", self.pos):
            self.pos += 4
            return True
        if self.text.startswith("false", self.pos):
            self.pos += 5
            return False
        if self.text.startswith("null", self.pos):
            self.pos += 4
            return None
        return self._number()

    def _string(self) -> str:
        self.pos += 1
        out = []
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char == '"':
                self.pos += 1
                return "".join(out)
            if char == "\\":
                self.pos += 1
                code = self.text[self.pos]
                if code == "u":
                    out.append(chr(int(self.text[self.pos + 1 : self.pos + 5], 16)))
                    self.pos += 5
                    continue
                out.append(_UNESCAPE.get(code, code))
                self.pos += 1
                continue
            out.append(char)
            self.pos += 1
        raise self._fail("unterminated string")

    def _number(self) -> object:
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos] in "-+.eE0123456789":
            self.pos += 1
        chunk = self.text[start : self.pos]
        if not chunk:
            raise self._fail("expected a value")
        if any(mark in chunk for mark in ".eE"):
            return float(chunk)
        return int(chunk)

    def _array(self) -> list:
        self.pos += 1
        items: list = []
        self._skip()
        if self.pos < len(self.text) and self.text[self.pos] == "]":
            self.pos += 1
            return items
        while True:
            items.append(self.value())
            self._skip()
            char = self.text[self.pos] if self.pos < len(self.text) else ""
            if char == ",":
                self.pos += 1
                continue
            if char == "]":
                self.pos += 1
                return items
            raise self._fail("expected , or ]")

    def _object(self) -> dict:
        self.pos += 1
        result: dict = {}
        self._skip()
        if self.pos < len(self.text) and self.text[self.pos] == "}":
            self.pos += 1
            return result
        while True:
            self._skip()
            key = self._string()
            self._skip()
            if self.text[self.pos] != ":":
                raise self._fail("expected :")
            self.pos += 1
            result[key] = self.value()
            self._skip()
            char = self.text[self.pos] if self.pos < len(self.text) else ""
            if char == ",":
                self.pos += 1
                continue
            if char == "}":
                self.pos += 1
                return result
            raise self._fail("expected , or }")


def decode(text: str) -> object:
    parser = _Parser(text)
    value = parser.value()
    parser._skip()
    if parser.pos != len(text):
        raise Torn(f"trailing content at position {parser.pos}")
    return value
