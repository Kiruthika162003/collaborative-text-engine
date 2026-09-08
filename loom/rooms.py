"""The rooms: every module and example announced by its own first sentence.

Hand-kept module lists rot by the second week, so the
directory walks the package and reads each room's opening
docstring line, correct by construction, a new room adding
its own row and a renamed one renaming it, with no list
anywhere to forget. The same walk covers the example days,
and those are held to one extra clerical standard, the run
instruction in the docstring, because an example that
cannot say how to run it is furniture. Undocumented rooms
are counted in the headline rather than hidden, a nameless
room in a workshop built on narration being a finding and
not a formatting preference, and the lobby and this
directory itself stay off the roster, a room that lists
itself being one mirror short of an infinite corridor.
"""

from __future__ import annotations

import importlib
import pkgutil

import examples
import loom

EXCLUDED = ("cli", "rooms")


def _walk(package, excluded=()) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for info in pkgutil.iter_modules(package.__path__):
        if info.ispkg or info.name in excluded:
            continue
        module = importlib.import_module(
            f"{package.__name__}.{info.name}"
        )
        doc = (module.__doc__ or "").strip()
        headline = (
            doc.splitlines()[0]
            if doc
            else "UNDOCUMENTED; a nameless room"
        )
        found.append((info.name, headline))
    return sorted(found)


def workshop() -> list[tuple[str, str]]:
    return _walk(loom, excluded=EXCLUDED)


def days() -> list[tuple[str, str]]:
    return _walk(examples)


def day_names() -> list[str]:
    return [name for name, _headline in days()]


def directory() -> str:
    rooms = workshop()
    nameless = sum(
        1
        for _name, headline in rooms
        if headline.startswith("UNDOCUMENTED")
    )
    lines = [
        f"{len(rooms)} room(s), {nameless} "
        "undocumented:"
    ]
    lines.extend(
        f"  {name}: {headline}"
        for name, headline in rooms
    )
    lines.append(
        "correct by construction; no list anywhere "
        "to forget"
    )
    return "\n".join(lines)


def itinerary() -> str:
    outings = days()
    missing = []
    for name, _headline in outings:
        module = importlib.import_module(
            f"examples.{name}"
        )
        if "python -m examples." not in (
            module.__doc__ or ""
        ):
            missing.append(name)
    lines = [f"{len(outings)} day(s) on record:"]
    lines.extend(
        f"  {name}: {headline}"
        for name, headline in outings
    )
    if missing:
        lines.append(
            "missing run instructions: "
            + ", ".join(missing)
            + "; an example that cannot say how to "
            "run it is furniture"
        )
    else:
        lines.append(
            "every day says how to run it; nothing "
            "here is furniture"
        )
    return "\n".join(lines)
