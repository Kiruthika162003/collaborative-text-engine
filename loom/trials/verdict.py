"""The verdict: what a trial claimed, what it measured, whether it held.

A trial is not a test. Tests pin small facts; a trial
stages a whole disagreement, replicas editing at cross
purposes, deliveries shuffled, and then measures whether
the loom's one promise held, that everyone ends at the
same cloth. The verdict records the claim in prose, the
numbers as measured, and a single boolean, and the
numbers stay even when they embarrass the claim, because
a trial whose evidence is tidied afterward is a press
release. Docstrings on the trials keep their corrected
guesses beside the measured truths in this repository's
standing tradition: the wrong guess, named as wrong, is
the part a reader learns from.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Verdict:
    trial: str
    claim: str
    numbers: dict[str, object]
    holds: bool

    def line(self) -> str:
        state = "holds" if self.holds else "BROKEN"
        return f"{self.trial}: {state}"

    def page(self) -> str:
        lines = [self.line(), f"claim: {self.claim}"]
        lines.extend(
            f"  {key} = {self.numbers[key]}"
            for key in sorted(self.numbers)
        )
        return "\n".join(lines)
