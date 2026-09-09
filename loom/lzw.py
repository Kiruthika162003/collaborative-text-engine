"""LZW: compress repetition by growing a dictionary of substrings the text keeps reusing.

Where Huffman coding shortens text by spending fewer bits on the
letters that recur, LZW shortens it by spending one code on a whole
substring that recurs. It reads the text building a dictionary:
starting with a code for each single symbol, it extends the current
run one symbol at a time as long as the run is already in the
dictionary, and the moment a run falls out of the dictionary it
emits the code for the longest part that was in, adds the new
longer run to the dictionary, and starts the next run from the
symbol that broke the streak. So the dictionary fills with exactly
the substrings the text repeats, and every later repetition of one
of them costs a single code instead of its full length, which is
why text thick with repeated phrases compresses well and text that
never repeats does not compress at all, since the dictionary never
gains an entry worth reusing. The decoder rebuilds the same
dictionary as it goes without being sent it, because it can derive
each new entry from the codes it has already seen, which is the
elegant part and also the source of the one subtle case: the
encoder can emit a code the decoder has not yet added, when a
pattern of the form symbol-run-symbol repeats immediately, and the
decoder handles it by knowing such a code must be the previous
entry with its own first symbol appended. I had guessed LZW and
Huffman would compress the same text about equally and that
choosing between them was a detail; they compress different things,
Huffman the skew in how often single symbols appear and LZW the
repetition of multi-symbol runs, so LZW wins on text full of
repeated substrings and Huffman on text with a lopsided alphabet,
and which one helps depends on which kind of redundancy the data
actually has, not on one being generally better. The dictionary
here starts from the distinct symbols the text uses, sorted so the
same text always yields the same codes, and that starting alphabet
travels with the codes so the decoder begins from the same base.
"""

from __future__ import annotations

from loom.errors import Invalid


def compress(text: str) -> tuple[str, list[int]]:
    if text == "":
        return "", []
    alphabet = "".join(sorted(set(text)))
    table = {symbol: index for index, symbol in enumerate(alphabet)}
    next_code = len(alphabet)
    codes: list[int] = []
    current = ""
    for symbol in text:
        combined = current + symbol
        if combined in table:
            current = combined
        else:
            codes.append(table[current])
            table[combined] = next_code
            next_code += 1
            current = symbol
    codes.append(table[current])
    return alphabet, codes


def decompress(alphabet: str, codes: list[int]) -> str:
    if not codes:
        return ""
    table = dict(enumerate(alphabet))
    next_code = len(alphabet)
    if codes[0] not in table:
        raise Invalid("the first code is not a known symbol")
    previous = table[codes[0]]
    result = [previous]
    for code in codes[1:]:
        if code in table:
            entry = table[code]
        elif code == next_code:
            entry = previous + previous[0]
        else:
            raise Invalid(f"code {code} refers to an entry that cannot exist yet")
        result.append(entry)
        table[next_code] = previous + entry[0]
        next_code += 1
        previous = entry
    return "".join(result)
