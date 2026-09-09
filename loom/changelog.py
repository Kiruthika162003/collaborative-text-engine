"""Changelog: build a Keep-a-Changelog document, versions and categorized entries.

A changelog has a shape the community settled on, versions
newest first, each grouping its entries under Added, Changed,
Deprecated, Removed, Fixed, and Security, and this builds one
to that shape so a caller records changes without remembering
the format. A version call opens a section, and the
category methods, added, changed, fixed, and the rest, file an
entry under the right heading of the current version, chaining
so a release records in one expression. Filing an entry before
any version is opened is refused, because an entry belongs to a
release and a changelog with floating entries under no version
is malformed in a way a caller wants caught rather than
rendered. The render orders the categories the standard way
regardless of the order the entries were filed, so a release
whose fix was recorded before its feature still renders Added
above Fixed, which is the order every reader of a changelog
expects, and it omits a category no entry used rather than
printing an empty heading, since a heading over nothing is
noise. The entries are held as data until render, so a caller
builds across the work of a release and renders once at the
end, and the render is the one place that knows the format, so
the same recorded changes could render to another format by
swapping the renderer. It records and renders and decides
nothing about version numbers or dates, which are the caller's
to supply, since only they know what the release is called.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid

CATEGORIES = (
    "Added",
    "Changed",
    "Deprecated",
    "Removed",
    "Fixed",
    "Security",
)


@dataclass
class Changelog:
    entries: list = field(default_factory=list)

    def version(self, tag: str, date: str = "") -> Changelog:
        self.entries.append({"version": tag, "date": date, "changes": {}})
        return self

    def _add(self, category: str, text: str) -> Changelog:
        if not self.entries:
            raise Invalid("open a version before adding an entry")
        self.entries[-1]["changes"].setdefault(category, []).append(text)
        return self

    def added(self, text: str) -> Changelog:
        return self._add("Added", text)

    def changed(self, text: str) -> Changelog:
        return self._add("Changed", text)

    def deprecated(self, text: str) -> Changelog:
        return self._add("Deprecated", text)

    def removed(self, text: str) -> Changelog:
        return self._add("Removed", text)

    def fixed(self, text: str) -> Changelog:
        return self._add("Fixed", text)

    def security(self, text: str) -> Changelog:
        return self._add("Security", text)

    def render(self) -> str:
        out = ["# Changelog"]
        for entry in self.entries:
            head = f"## {entry['version']}"
            if entry["date"]:
                head += f" - {entry['date']}"
            out.append(head)
            for category in CATEGORIES:
                items = entry["changes"].get(category)
                if items:
                    out.append(f"### {category}")
                    out.extend(f"- {item}" for item in items)
        return "\n".join(out)
