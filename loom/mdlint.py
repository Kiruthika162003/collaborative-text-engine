"""Markdown lint: the common style checks, each a rule with a code, gathered into one pass.

A style linter for Markdown runs a handful of rules that
catch the mechanical slips a renderer tolerates but a reader
and a diff notice, and this gathers them, each rule carrying a
short code so a caller can point at one, quiet one, or fix
one. The rules reuse the organs that already know these
things: the headings module reports a level a heading skipped,
the bullet-style module whether the markers are mixed, the
renumber module whether an ordered list's numbers drifted, and
two simple local scans catch trailing whitespace and hard
tabs and runs of blank lines. It reports and does not fix,
because the fixers already exist as their own operations and a
linter's job is to say what is wrong, not to decide when to
change the document; a caller who wants the fix calls the
fixer. The rule set is a common subset, not the whole of any
published linter's catalogue, and it says so, because
claiming completeness it does not have would be the worst kind
of lint, the one that lets a writer believe a clean pass means
more than it does. Findings are ordered by line so a writer
reads them top to bottom the way they would fix them, with the
document-wide rules that name no single line gathered where
they do not interrupt that reading.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.author import Author
from loom.bulletstyle import is_uniform
from loom.headings import headings
from loom.renumber import needs_renumber


@dataclass(frozen=True)
class Finding:
    code: str
    line: int
    message: str


def lint(author: Author) -> list[Finding]:
    weave = author.weave
    lines = weave.text().split("\n")
    findings: list[Finding] = []

    for heading in headings(weave):
        if heading.gap:
            findings.append(
                Finding("MD-GAP", -1, f"heading {heading.title!r} skips a level")
            )
    if not is_uniform(author):
        findings.append(Finding("MD-BULLET", -1, "mixed bullet markers"))
    if needs_renumber(author):
        findings.append(
            Finding("MD-NUM", -1, "ordered list numbers are off")
        )
    for index, line in enumerate(lines):
        if line != line.rstrip():
            findings.append(Finding("MD-TRAIL", index, "trailing whitespace"))
        if "\t" in line:
            findings.append(Finding("MD-TAB", index, "hard tab"))
    run = 0
    for index, line in enumerate(lines):
        if line.strip() == "":
            run += 1
            if run == 2:
                findings.append(
                    Finding("MD-BLANK", index, "multiple consecutive blank lines")
                )
        else:
            run = 0
    return sorted(findings, key=lambda finding: (finding.line, finding.code))


def clean(author: Author) -> bool:
    return not lint(author)


def report(author: Author) -> str:
    findings = lint(author)
    if not findings:
        return "markdown clean; the common style checks pass"
    lines = [f"{len(findings)} issue(s):"]
    for finding in findings:
        where = f"line {finding.line}" if finding.line >= 0 else "document"
        lines.append(f"  [{finding.code}] {where}: {finding.message}")
    lines.append("a common subset, not a full linter; reports, does not fix")
    return "\n".join(lines)
