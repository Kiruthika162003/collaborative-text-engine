"""Squeeze: a codec chaining the transform, move-to-front, and run coding into one packer.

This is the whole compression pipeline the earlier pieces were
building toward, wired end to end. It puts a text through the
Burrows-Wheeler transform, which reorders the characters so that
ones with shared context cluster into runs; then through
move-to-front, which turns those runs and locally frequent
characters into small numbers, especially long stretches of zeros;
then through a run coder that collapses each run of zeros into the
value zero followed by the run's length, which is where the text
actually gets smaller. Unpacking runs the three stages in reverse,
expanding the zero runs, undoing move-to-front, and inverting the
transform back to the original text, exactly. I had guessed each
stage would compress a little and the savings would add up across
them; that is not how it works, and seeing it wired together made
the point clearly. The transform and move-to-front change no
lengths at all, not one character fewer comes out of either than
went in, so measured on their own they look useless. All the
shrinkage happens in the single run-coding stage at the end, and it
happens there only because the two stages before it arranged the
data into the long zero runs that stage can collapse. So the
pipeline's value is not spread across it but concentrated in the
last step, with the earlier steps being setup whose worth is
invisible until the end and would be zero without the step that
follows. That is the honest way to read it: the transform earns its
keep not by compressing but by making the later compression
possible, which is why it is measured here by how far the final
token count falls below the character count of the input rather than
by anything the transform reports on its own. The run coding is
unambiguous because a zero always announces a run and is always
followed by its count, so a genuine single zero is stored as a run
of length one rather than being confused with the count that
follows it.
"""

from __future__ import annotations

from loom import bwt, mtf


def _pack_zero_runs(codes: list[int]) -> list[int]:
    packed: list[int] = []
    index = 0
    while index < len(codes):
        if codes[index] == 0:
            run = index
            while run < len(codes) and codes[run] == 0:
                run += 1
            packed.append(0)
            packed.append(run - index)
            index = run
        else:
            packed.append(codes[index])
            index += 1
    return packed


def _unpack_zero_runs(tokens: list[int]) -> list[int]:
    codes: list[int] = []
    index = 0
    while index < len(tokens):
        if tokens[index] == 0:
            codes.extend([0] * tokens[index + 1])
            index += 2
        else:
            codes.append(tokens[index])
            index += 1
    return codes


def squeeze(text: str) -> tuple[str, list[int]]:
    transformed = bwt.transform(text)
    alphabet, codes = mtf.encode(transformed)
    return alphabet, _pack_zero_runs(codes)


def unsqueeze(alphabet: str, tokens: list[int]) -> str:
    codes = _unpack_zero_runs(tokens)
    transformed = mtf.decode(alphabet, codes)
    return bwt.inverse(transformed)


def token_count(text: str) -> int:
    _, tokens = squeeze(text)
    return len(tokens)
