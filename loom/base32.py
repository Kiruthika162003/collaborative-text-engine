"""Base32: bytes as a string of case-insensitive letters and digits, five bits at a time.

Base32 encodes arbitrary bytes into text drawn from a
thirty-two-character alphabet, the letters A to Z and the digits 2
to 7, by regrouping the input's bits: it reads the bytes as a
continuous stream of bits and slices that stream into five-bit
pieces, each piece naming one alphabet character, since thirty-two
is two to the fifth. Because eight and five share no common factor,
the grouping only lines up every forty bits, that is, every five
input bytes become exactly eight output characters, and when the
input does not end on a five-byte boundary the last group is
padded, both the trailing bits filled out to a full character and
the output filled with the equals sign to a multiple of eight, so a
decoder knows where the real bits stop. Decoding reverses it, mapping
each character back to five bits, concatenating them, and reading
off whole bytes, discarding the padding bits that were only there to
finish the last character. I had guessed base32 was simply a worse
base64, wasting more space for no reason; it does expand more, eight
characters for every five bytes where base64 spends four for every
three, but the alphabet is the point of the trade. Every character
is a letter or a digit with no punctuation and no case distinction
that matters, so base32 survives being read aloud, written by hand,
typed without a shift key, or put where base64's mixed case and its
plus and slash would be mangled or misread, which is why it is used
for things humans handle directly. So the extra size buys
robustness in transcription rather than being waste, and that is the
honest reason to choose it over the denser encoding. This uses the
standard alphabet and padding so its output matches the encoding
libraries produce, and it rejects a character outside the alphabet
rather than decoding it as something arbitrary.
"""

from __future__ import annotations

from loom.errors import Invalid

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
_LOOKUP = {char: index for index, char in enumerate(ALPHABET)}


def encode(data: bytes) -> str:
    bits = 0
    held = 0
    out = []
    for byte in data:
        bits = (bits << 8) | byte
        held += 8
        while held >= 5:
            held -= 5
            out.append(ALPHABET[(bits >> held) & 0x1F])
    if held > 0:
        out.append(ALPHABET[(bits << (5 - held)) & 0x1F])
    while len(out) % 8 != 0:
        out.append("=")
    return "".join(out)


def decode(text: str) -> bytes:
    trimmed = text.rstrip("=")
    bits = 0
    held = 0
    out = bytearray()
    for char in trimmed:
        if char not in _LOOKUP:
            raise Invalid(f"{char!r} is not a base32 character")
        bits = (bits << 5) | _LOOKUP[char]
        held += 5
        if held >= 8:
            held -= 8
            out.append((bits >> held) & 0xFF)
    return bytes(out)
