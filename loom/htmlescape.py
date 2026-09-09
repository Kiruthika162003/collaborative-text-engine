"""HTML escape: protect the five characters that break HTML, and undo it exactly.

Dropping text into HTML is unsafe if it holds an angle
bracket or an ampersand, because the browser reads them as
markup, so this escapes the five characters that matter, the
ampersand, the two angle brackets, and the two quotes, into
their named or numeric entities, and unescapes them back. The
order is the subtle part and it is handled: escaping does the
ampersand first, because every other entity contains one and
escaping them first would then double-escape those ampersands
into gibberish; unescaping reverses it, decoding the named
entities before the bare ampersand for the same reason from
the other direction. The result is a clean round trip, text
escaped for HTML and unescaped back returns exactly what went
in, which is the contract that lets a value cross into an HTML
context and come home unchanged. The scope is the five
entities HTML needs for text content and attribute values,
the ones a serializer must produce; it does not decode the
hundreds of named entities a full HTML parser knows, because
producing only these five and decoding only these five keeps
escape and unescape true inverses, where handling more on the
way in than the way out would break the round trip it
promises. The two functions are pure, and being each other's
inverse is the whole of the contract worth keeping.
"""

from __future__ import annotations

NAMED = (
    ("<", "&lt;"),
    (">", "&gt;"),
    ('"', "&quot;"),
    ("'", "&#39;"),
)


def escape(text: str) -> str:
    text = text.replace("&", "&amp;")
    for char, entity in NAMED:
        text = text.replace(char, entity)
    return text


def unescape(text: str) -> str:
    for char, entity in NAMED:
        text = text.replace(entity, char)
    return text.replace("&amp;", "&")


def needs_escape(text: str) -> bool:
    return any(char in text for char in "&<>\"'")
