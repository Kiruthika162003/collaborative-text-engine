"""Rlestring: run-length coding of a string into character-and-count runs, and back.

Run-length coding replaces each maximal run of one repeated
character with that character and the length of the run, so a
string of long stretches of sameness turns into a short list of
runs. Encoding walks the string once, extending the current run
while the character stays the same and closing it off with its
length when the character changes; decoding expands each run back
to its characters. It is exact and reverses cleanly, and its whole
value depends on the shape of the input. I had assumed run-length
coding was a compression that always helped a little; it does not,
and on ordinary text it hurts. A string with few repeats has a run
of length one for nearly every character, so the encoding stores a
count of one beside each character and comes out roughly twice the
size of the original, larger, not smaller. It saves space only when
runs are genuinely long, which is why it is applied to data
arranged to have long runs, the output of the Burrows-Wheeler and
move-to-front stages, or bitmap scanlines of flat color, and not to
prose, where it is a waste. So the honest way to describe it is not
as compression but as compression conditional on the input already
being runny, a stage that pays off downstream of something that
creates the runs rather than on its own. This keeps the runs as
explicit character-and-count pairs rather than splicing them into a
string, which would be ambiguous whenever the text itself contains
digits, since a decoder could not tell a run count from a digit that
was part of the data; the pair form has no such ambiguity and
round-trips any string at all.
"""

from __future__ import annotations

from loom.errors import Invalid


def encode(text: str) -> list[tuple[str, int]]:
    runs: list[tuple[str, int]] = []
    for char in text:
        if runs and runs[-1][0] == char:
            previous, count = runs[-1]
            runs[-1] = (previous, count + 1)
        else:
            runs.append((char, 1))
    return runs


def decode(runs: list[tuple[str, int]]) -> str:
    out = []
    for char, count in runs:
        if count < 1:
            raise Invalid("a run length must be at least one")
        if len(char) != 1:
            raise Invalid("a run must name a single character")
        out.append(char * count)
    return "".join(out)


def run_count(text: str) -> int:
    return len(encode(text))
