"""Hex dump: render bytes as the offset, hex, and ASCII view every debugger shows.

When bytes must be read by a human, the hex dump is the format
that works, three columns per row: the offset of the row in the
data, the bytes as two-digit hex separated by spaces, and the
same bytes as printable ASCII with the unprintable ones shown as
dots. This renders that, a row per width bytes, the hex column
padded to a fixed width so the ASCII column lines up whether the
last row is full or short, which is what makes a dump scannable
down its columns rather than ragged. The printable range is the
usual one, space through tilde, and everything outside it, a
control byte or a high byte, becomes a dot in the ASCII column,
because showing a raw control character would move the cursor or
mangle the row and a dot holds the place without lying about
what is there beyond that it is not printable. The width is the
caller's, sixteen by default, the width that fits a common
terminal and matches what most tools emit, so a dump from here
sits comfortably beside one from elsewhere. It is a rendering
that reads bytes and writes text and changes nothing, a way of
looking at data rather than a transform of it, and it handles
the empty input by rendering nothing rather than an offset row
for bytes that are not there, since a dump of no bytes is no
rows, not a row of zero bytes.
"""

from __future__ import annotations


def dump(data: bytes, width: int = 16) -> str:
    rows = []
    for offset in range(0, len(data), width):
        chunk = data[offset : offset + width]
        hex_part = " ".join(f"{byte:02x}" for byte in chunk)
        hex_part = hex_part.ljust(width * 3 - 1)
        ascii_part = "".join(
            chr(byte) if 32 <= byte < 127 else "." for byte in chunk
        )
        rows.append(f"{offset:08x}  {hex_part}  |{ascii_part}|")
    return "\n".join(rows)


def hex_only(data: bytes, width: int = 16) -> str:
    return "\n".join(
        " ".join(f"{byte:02x}" for byte in data[offset : offset + width])
        for offset in range(0, len(data), width)
    )
