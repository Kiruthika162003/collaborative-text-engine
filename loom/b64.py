"""Base64: encode bytes to base64 text and decode it back, built from the bits up.

Base64 packs binary into text that survives channels that mangle
raw bytes, and this implements it from the bit level rather than
delegating, because an engine that stores and moves data
benefits from owning the transform. Encoding takes bytes three
at a time, twenty-four bits, and splits them into four six-bit
groups, each an index into the sixty-four-character alphabet;
when the input does not divide evenly the last group is padded
with equals signs, one for a two-byte tail and two for a one-
byte tail, so the length always comes out a multiple of four
and a decoder knows how many real bytes the tail held. Decoding
reverses it, reading the six-bit values back and reassembling
the bytes, dropping the padding bits that the equals signs stood
for, so the round trip is exact: any bytes encoded and decoded
return unchanged, which is the whole promise of an encoding.
Whitespace in the input is ignored on decode, because base64 is
often wrapped to a line width and the newlines are not data, and
a character outside the alphabet is refused rather than skipped,
because a stray character means the text is corrupted or not
base64 at all and reading past it would return bytes the text
does not actually encode. It is the standard alphabet with plus
and slash, the common one, not the URL-safe variant with dash
and underscore, which is a different alphabet a caller wanting
it asks for by name rather than getting by surprise.
"""

from __future__ import annotations

from loom.errors import Invalid

ALPHABET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789+/"
)
INVERSE = {char: index for index, char in enumerate(ALPHABET)}


def encode(data: bytes) -> str:
    out = []
    for start in range(0, len(data), 3):
        chunk = data[start : start + 3]
        packed = int.from_bytes(chunk + b"\x00" * (3 - len(chunk)), "big")
        chars = [
            ALPHABET[(packed >> 18) & 63],
            ALPHABET[(packed >> 12) & 63],
            ALPHABET[(packed >> 6) & 63],
            ALPHABET[packed & 63],
        ]
        for pad in range(3 - len(chunk)):
            chars[3 - pad] = "="
        out.extend(chars)
    return "".join(out)


def decode(text: str) -> bytes:
    clean = "".join(text.split()).rstrip("=")
    out = bytearray()
    for start in range(0, len(clean), 4):
        group = clean[start : start + 4]
        bits = 0
        value = 0
        for char in group:
            if char not in INVERSE:
                raise Invalid(f"{char!r} is not a base64 character")
            value = (value << 6) | INVERSE[char]
            bits += 6
        value >>= bits % 8
        byte_count = bits // 8
        if byte_count:
            out += value.to_bytes(byte_count, "big")
    return bytes(out)
