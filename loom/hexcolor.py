"""Hex color: parse and render CSS hex colors, and judge their lightness.

Colors on the web are hex strings, and this reads and writes
them and answers the one question a caller styling text keeps
asking, is this color dark or light. Parsing accepts both the
three-digit short form and the six-digit long form, expanding
each short digit to a doubled pair the way CSS does so that the
letter f short means the same as ff long, and returns the red,
green, and blue as integers zero to two hundred fifty-five.
Rendering is the inverse, the six-digit lowercase form, and the
two round-trip through the long form. The lightness judgment
uses relative luminance, the weighted sum of the channels that
matches how the eye perceives brightness, green counting far
more than blue because the eye is more sensitive to it, which is
why a pure green looks lighter than a pure blue of the same
numeric value. Whether a color is dark is then a threshold on
that luminance, and the threshold is a convention this states
rather than a fact, because the boundary between dark and light
is a judgment a designer sometimes wants to move; the default is
the middle of the range and a caller who needs a different cut
passes their own. The luminance is a perceptual weighting, not
the full sRGB-to-linear conversion the accessibility standards
use for contrast ratios, and that is named, because a caller
computing WCAG contrast needs the stricter formula and this
lighter one would give them a slightly wrong answer they should
know to avoid.
"""

from __future__ import annotations

from loom.errors import Invalid


def parse(text: str) -> tuple[int, int, int]:
    body = text.lstrip("#").strip().lower()
    if len(body) == 3:
        body = "".join(char * 2 for char in body)
    if len(body) != 6 or any(char not in "0123456789abcdef" for char in body):
        raise Invalid(f"{text!r} is not a hex color")
    return (int(body[0:2], 16), int(body[2:4], 16), int(body[4:6], 16))


def to_hex(red: int, green: int, blue: int) -> str:
    return f"#{red:02x}{green:02x}{blue:02x}"


def luminance(red: int, green: int, blue: int) -> float:
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def is_dark(text: str, threshold: float = 128.0) -> bool:
    return luminance(*parse(text)) < threshold
