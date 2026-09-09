"""INI file: parse and render the sectioned key-value config format.

The INI format is the simplest config a program keeps, named
sections in square brackets each holding key-equals-value
lines, and this reads and writes it. Keys before any section
header belong to a default section, the top-of-file settings a
flat config uses, and this keeps them under an empty section
name so they round-trip back to the top without a header.
Comments, lines opening with a semicolon or a hash, are skipped
on read and not preserved on write, which is the honest limit
of a parser that keeps a structure rather than a document: it
reads the settings, not the annotations around them, and a
caller who needs the comments kept wants a format-preserving
editor, not this. Values are strings, because INI carries no
types and a parser that guessed would turn a port number into
an int and a version string into a float; a caller coerces on
the way out knowing what it expects. A duplicate key within a
section resolves to the last, the common convention, and
rendering writes the default section's keys first so they land
at the top where they parse back from. The round trip holds for
the structure: parse a config, render it, and parse again
returns the same sections and keys, with the whitespace around
the equals normalized to one space each side, which is stated
so a caller diffing the output against a hand-spaced original
is not surprised by the spacing this chooses.
"""

from __future__ import annotations

DEFAULT = ""


def parse(text: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {DEFAULT: {}}
    section = DEFAULT
    for raw in text.split("\n"):
        line = raw.strip()
        if not line or line[0] in ";#":
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            result.setdefault(section, {})
        elif "=" in line:
            key, _, value = line.partition("=")
            result[section][key.strip()] = value.strip()
    if not result[DEFAULT]:
        del result[DEFAULT]
    return result


def render(config: dict[str, dict[str, str]]) -> str:
    ordered = []
    if DEFAULT in config:
        ordered.append((DEFAULT, config[DEFAULT]))
    for section, values in config.items():
        if section != DEFAULT:
            ordered.append((section, values))
    blocks = []
    for section, values in ordered:
        lines = []
        if section:
            lines.append(f"[{section}]")
        for key, value in values.items():
            lines.append(f"{key} = {value}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def get(
    config: dict[str, dict[str, str]],
    section: str,
    key: str,
    default: str = "",
) -> str:
    return config.get(section, {}).get(key, default)
