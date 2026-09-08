"""Every trial, one docket, no verdict summarized away."""

from __future__ import annotations

import importlib

from loom.trials.verdict import Verdict

TRIALS = (
    "loom.trials.duet",
    "loom.trials.stormtrial",
    "loom.trials.deltabill",
    "loom.trials.gravetrial",
    "loom.trials.undotrial",
    "loom.trials.interleavetrial",
    "loom.trials.marktrial",
    "loom.trials.longhaul",
    "loom.trials.sessiontrial",
    "loom.trials.mergetrial",
)


def all_verdicts() -> list[Verdict]:
    found = []
    for dotted in TRIALS:
        module = importlib.import_module(dotted)
        found.append(module.run())
    return found


def broken() -> list[str]:
    return [
        verdict.trial
        for verdict in all_verdicts()
        if not verdict.holds
    ]


def docket() -> str:
    verdicts = all_verdicts()
    lines = [verdict.line() for verdict in verdicts]
    failing = sum(
        1 for verdict in verdicts if not verdict.holds
    )
    lines.append("")
    lines.append(
        f"{len(verdicts)} trial(s), {failing} broken"
    )
    return "\n".join(lines)
