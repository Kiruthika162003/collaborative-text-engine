"""The storm: seeded weather for the loom, every gust replayable.

Handwritten scenarios test what their author feared; storms
test what nobody thought of, thousands of small gestures
drawn from a seeded generator so any wreckage can be
revisited by number. A gust is one plausible human act,
typing a short burst at a position that exists or erasing
a stretch that exists, weighted toward typing because
documents grow, and gusts never mint impossible gestures,
the generator asking the author's own weave what positions
are real before choosing one, since a storm that breaks
the rules of physics proves nothing about houses. The
storm drives a circle: each round one author gusts and
speaks, deliveries happen on a seeded cadence mid-storm so
operations cross in flight, and the final settle brings
the dust down. What the storm returns is a bill, gusts
thrown, glyphs typed, glyphs erased, deliveries
mid-flight, and the bill is the trial's evidence table.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from loom.author import Author
from loom.circle import Circle
from loom.errors import Invalid

ALPHABET = "abcdefghijklmnop "
TYPE_WEIGHT = 3
MAX_BURST = 4
DELIVER_EVERY = 5


def gust(
    author: Author, dice: random.Random
) -> list:
    length = author.weave.visible_count()
    can_erase = length > 0
    typing = (
        not can_erase
        or dice.randrange(TYPE_WEIGHT + 1) > 0
    )
    if typing:
        position = dice.randrange(length + 1)
        burst = "".join(
            dice.choice(ALPHABET)
            for _ in range(
                1 + dice.randrange(MAX_BURST)
            )
        )
        return author.type_at(position, burst)
    position = dice.randrange(length)
    count = 1 + dice.randrange(
        min(MAX_BURST, length - position)
    )
    return author.erase_at(position, count)


@dataclass
class Storm:
    rounds: int
    seed: int
    typed: int = 0
    erased: int = 0
    mid_flight_deliveries: int = 0
    ledger: dict[str, int] = field(default_factory=dict)

    def blow_through(self, circle: Circle) -> str:
        if self.rounds < 1:
            raise Invalid(
                "a storm of zero rounds is weather in "
                "a forecast"
            )
        dice = random.Random(self.seed)
        sites = sorted(circle.authors)
        for round_number in range(self.rounds):
            site = dice.choice(sites)
            ops = gust(circle.author(site), dice)
            for op in ops:
                if hasattr(op, "glyph"):
                    self.typed += 1
                else:
                    self.erased += 1
            circle.say(site, ops)
            if round_number % DELIVER_EVERY == (
                DELIVER_EVERY - 1
            ):
                link = circle.links[
                    dice.choice(
                        sorted(circle.links)
                    )
                ]
                if link.deliver_batch():
                    self.mid_flight_deliveries += 1
        settle_report = circle.settle()
        self.ledger = {
            "rounds": self.rounds,
            "typed": self.typed,
            "erased": self.erased,
            "mid_flight": self.mid_flight_deliveries,
        }
        return (
            f"storm of {self.rounds} round(s): "
            f"{self.typed} glyph(s) typed, "
            f"{self.erased} erased, "
            f"{self.mid_flight_deliveries} mid-flight "
            f"delivery(ies); {settle_report}"
        )
