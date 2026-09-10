"""MTF: move-to-front, turning locally repeated symbols into small numbers a coder can shrink.

Move-to-front keeps an ordered table of the symbols and codes each
symbol of the text by its current position in that table, then
moves that symbol to the front. A symbol that has just appeared is
therefore at position zero, so the next occurrence of the same
symbol codes as zero, and a run of one symbol becomes a run of
zeros, while a symbol seen recently but not last sits near the
front and codes as a small number. Text where the same few symbols
recur close together, which is exactly what the Burrows-Wheeler
transform produces, comes out of move-to-front as a stream heavy
with zeros and small values. I had guessed move-to-front was itself
a compressor; it is not, it changes no lengths at all, the output
has exactly as many numbers as the input had symbols, and it can
even be applied and undone with the text unchanged in size. What it
does is change the distribution: it converts locality, the tendency
of a symbol to reappear soon after it appeared, into numeric
smallness, and smallness is what an entropy coder like Huffman
rewards with short codes. So its whole worth is as a stage between
the transform that creates the locality and the coder that cashes
it in, and on its own it neither shrinks nor grows anything, which
is the honest way to describe it rather than calling it
compression. It is exactly reversible because the decoder keeps the
same table and makes the same move after reading each position, so
the two tables stay in step and each code names the symbol the
encoder meant; the starting table is the sorted distinct symbols of
the text, and it travels with the codes so the decoder starts from
the same order.
"""

from __future__ import annotations

from loom.errors import Invalid


def encode(data: str) -> tuple[str, list[int]]:
    table = sorted(set(data))
    alphabet = "".join(table)
    codes = []
    for symbol in data:
        position = table.index(symbol)
        codes.append(position)
        table.pop(position)
        table.insert(0, symbol)
    return alphabet, codes


def decode(alphabet: str, codes: list[int]) -> str:
    table = list(alphabet)
    out = []
    for code in codes:
        if not 0 <= code < len(table):
            raise Invalid(f"code {code} is outside the table")
        symbol = table[code]
        out.append(symbol)
        table.pop(code)
        table.insert(0, symbol)
    return "".join(out)
