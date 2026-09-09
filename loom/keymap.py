"""Keymap: key chords bound to named commands, with conflicts surfaced not swallowed.

An editor's keymap is a lookup from a chord to a command,
and the trouble it hides is ordering: a writer binds a
command to ctrl+shift+b and another to shift+ctrl+b and
believes they are two chords when a keyboard sends one. So
every chord is normalised before it is stored or compared,
its modifiers lowercased, dealiased, deduplicated, and put
in a fixed order, and its one non-modifier key checked to be
exactly one, because a chord with no key or two keys is not
a chord a keyboard can send and pretending otherwise stores
a binding that never fires. With normalisation in place a
rebind that would shadow an existing command under the same
real chord is a conflict, and it is raised rather than
resolved by last-writer, because a keymap that silently lets
the second binding win is how a writer loses a shortcut they
still rely on and cannot find why. Rebinding on purpose has
its own verb, so overriding is possible but never
accidental, and merging two keymaps unions them but stops at
the same conflict, since two people's shortcuts colliding is
a decision for them, not a coin toss the merge makes on
their behalf. The cheat sheet renders the bindings in chord
order so a writer can read what their hands already know.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Diverged, Invalid

MODIFIER_ORDER = ("ctrl", "alt", "shift", "cmd")
ALIASES = {
    "control": "ctrl",
    "option": "alt",
    "opt": "alt",
    "meta": "cmd",
    "command": "cmd",
    "win": "cmd",
    "super": "cmd",
}


def normalize(chord: str) -> str:
    parts = [
        ALIASES.get(piece.strip().lower(), piece.strip().lower())
        for piece in chord.split("+")
        if piece.strip()
    ]
    modifiers = {part for part in parts if part in MODIFIER_ORDER}
    keys = [part for part in parts if part not in MODIFIER_ORDER]
    if len(keys) != 1:
        raise Invalid(
            f"{chord!r} is not a chord a keyboard can send; a "
            "chord needs exactly one non-modifier key"
        )
    ordered = [mod for mod in MODIFIER_ORDER if mod in modifiers]
    return "+".join(ordered + keys)


@dataclass(frozen=True)
class Binding:
    chord: str
    command: str
    description: str = ""


@dataclass
class Keymap:
    bindings: dict[str, Binding] = field(default_factory=dict)

    def bind(
        self, chord: str, command: str, description: str = ""
    ) -> str:
        norm = normalize(chord)
        existing = self.bindings.get(norm)
        if existing is not None and existing.command != command:
            raise Diverged(
                f"chord {norm!r} already runs {existing.command!r}; "
                "binding it to another command is a conflict, not "
                "a rebind. Use rebind to override on purpose"
            )
        self.bindings[norm] = Binding(norm, command, description)
        return f"{norm} runs {command}"

    def rebind(
        self, chord: str, command: str, description: str = ""
    ) -> str:
        norm = normalize(chord)
        self.bindings[norm] = Binding(norm, command, description)
        return f"{norm} now runs {command}"

    def unbind(self, chord: str) -> bool:
        return self.bindings.pop(normalize(chord), None) is not None

    def resolve(self, chord: str) -> str | None:
        binding = self.bindings.get(normalize(chord))
        return binding.command if binding is not None else None

    def merge(self, other: Keymap) -> Keymap:
        merged = Keymap(dict(self.bindings))
        for binding in other.bindings.values():
            merged.bind(
                binding.chord, binding.command, binding.description
            )
        return merged

    def cheat_sheet(self) -> str:
        if not self.bindings:
            return "no bindings; the keymap is empty"
        lines = []
        for chord in sorted(self.bindings):
            binding = self.bindings[chord]
            tail = f"  ({binding.description})" if binding.description else ""
            lines.append(f"{chord}: {binding.command}{tail}")
        return "\n".join(lines)
