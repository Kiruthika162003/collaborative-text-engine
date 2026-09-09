"""CRC-32: the checksum, computed from its polynomial by the table method.

A CRC-32 is the checksum zip files and network frames use to
catch corruption, and this computes it from scratch, building
the lookup table from the standard polynomial and then running
the byte-at-a-time algorithm that every fast implementation
uses. The table holds, for each possible byte, the result of
feeding it through the polynomial eight bits at a time, computed
once at import; the checksum then processes each input byte with
a single table lookup and a shift rather than eight bit
operations, which is the whole point of the table. It uses the
reflected polynomial and the initial and final inversion that
the common CRC-32 specifies, the one zlib and gzip and PNG all
agree on, so a checksum computed here matches the checksum those
tools compute for the same bytes, which is what makes it useful
for verifying data that crossed one of them. A seed can be
passed to continue a checksum across chunks, so a large input
split into pieces checksums to the same value as the whole, the
property a streaming caller needs. It is a checksum, not a hash
for security: CRC-32 catches accidental corruption well and
resists deliberate tampering not at all, since an attacker can
adjust bytes to hold the checksum constant, and that distinction
is stated because reaching for a CRC where a cryptographic hash
is needed is a real and dangerous mistake. For its actual job,
telling whether bytes arrived intact, it is exactly right.
"""

from __future__ import annotations

POLYNOMIAL = 0xEDB88320


def _build_table() -> list[int]:
    table = []
    for index in range(256):
        value = index
        for _ in range(8):
            if value & 1:
                value = (value >> 1) ^ POLYNOMIAL
            else:
                value >>= 1
        table.append(value)
    return table


TABLE = _build_table()


def crc32(data: bytes, seed: int = 0) -> int:
    crc = seed ^ 0xFFFFFFFF
    for byte in data:
        crc = TABLE[(crc ^ byte) & 0xFF] ^ (crc >> 8)
    return crc ^ 0xFFFFFFFF


def hex_crc32(data: bytes) -> str:
    return f"{crc32(data):08x}"
