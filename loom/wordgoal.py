"""Word goal: a target, live progress, and milestones that fire once.

Writers set a word count and want to know how close they
are without the tool nagging, and the goal tracker gives
them the honest arithmetic: words written against words
targeted, the percentage, and how many remain, all read
from the living cloth so deleting a paragraph correctly
walks the progress backward rather than pretending the
words are banked. Milestones, the quarter marks and the
finish, fire exactly once each and only when first crossed
upward, because a milestone that re-fires every time the
count wobbles across it is a notification the writer learns
to mute, and a muted milestone is a milestone that failed.
Crossing a milestone downward by deleting does not un-fire
it, because the writer was congratulated for reaching it
and clawing that back is the tool being petty, but it does
re-arm so that re-crossing upward is quiet, since the news
is no longer news. Overshooting the goal is celebrated, not
capped, because a writer who blew past their target has
done more, not something wrong, and the tracker reports the
surplus rather than pretending at a hundred percent.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.concordance import frequencies
from loom.errors import Invalid
from loom.weave import Weave

MILESTONES = (25, 50, 75, 100)


@dataclass
class WordGoal:
    weave: Weave
    target: int
    fired: set = field(default_factory=set)

    def __post_init__(self) -> None:
        if self.target < 1:
            raise Invalid(
                "a goal of zero words is a finished "
                "goal before the first keystroke"
            )

    def written(self) -> int:
        return sum(frequencies(self.weave).values())

    def percent(self) -> int:
        return self.written() * 100 // self.target

    def remaining(self) -> int:
        return max(0, self.target - self.written())

    def check_milestones(self) -> list[int]:
        reached = self.percent()
        newly = []
        for milestone in MILESTONES:
            if (
                reached >= milestone
                and milestone not in self.fired
            ):
                self.fired.add(milestone)
                newly.append(milestone)
            elif (
                reached < milestone
                and milestone in self.fired
            ):
                self.fired.discard(milestone)
        return newly

    def report(self) -> str:
        written = self.written()
        pct = self.percent()
        if written >= self.target:
            surplus = written - self.target
            return (
                f"{written} of {self.target} words, "
                f"goal met with {surplus} to spare; "
                "overshooting is doing more, not "
                "something wrong"
            )
        return (
            f"{written} of {self.target} words "
            f"({pct}%), {self.remaining()} to go"
        )
