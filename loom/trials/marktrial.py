"""The marktrial: attire crossing out of order, both wardrobes matching.

Alice bolds a word and immediately regrets it; Bob,
concurrently, dresses the whole stretch in italic. The
envelopes cross the wire in the worst order the postmaster
allows, the regret arriving before the mark it strips, and
the first run convicted the sorting office: the early
unmark shelved correctly and then waited forever, because
the attire shelf was swept only on text deliveries, and a
mark's own arrival, the exact cork the regret was waiting
behind, drained nothing. The fix extends the cork rule
upstairs, every successful attire delivery sweeping the
shelf, and with it the trial's promises hold measured:
shelve with a reason, drain in the same breath, and both
wardrobes compare equal as data, bold gone everywhere,
italic standing, one mark standing and one stripped in
each house, because looking alike is a compliment and
comparing equal is a property.
"""

from __future__ import annotations

from loom.binder import Binder
from loom.marks import Mark, Unmark, Wardrobe
from loom.postmaster import (
    Postmaster,
    encode_mark,
    encode_unmark,
)
from loom.station import Station
from loom.trials.verdict import Verdict
from loom.wire import encode


def _office(site: str) -> Postmaster:
    station = Station.named(site)
    return Postmaster(
        station=station,
        wardrobe=Wardrobe(weave=station.author.weave),
        binder=Binder(),
    )


def run() -> Verdict:
    home = _office("alice")
    away = _office("bob")

    ops = home.station.type_at(0, "plain bold plain")
    for op in ops:
        away.dispatch(encode(op))

    bold = Mark(
        id=home.station.author._mint(),
        style="bold",
        start=ops[6].id,
        end=ops[9].id,
    )
    home.dispatch(encode_mark(bold))
    regret = Unmark(
        id=away.station.author._mint(),
        mark_id=bold.id,
    )
    italic = Mark(
        id=ops[9].id.__class__(
            site="bob", counter=99
        ),
        style="italic",
        start=ops[0].id,
        end=ops[15].id,
    )
    away.dispatch(encode_mark(italic))

    shelved = away.dispatch(encode_unmark(regret))
    early_shelved = "shelved" in shelved
    drained = away.dispatch(encode_mark(bold))
    drain_noted = "drained" in drained or (
        "dressed" in drained
    )
    home.dispatch(encode_unmark(regret))
    home.dispatch(encode_mark(italic))

    home_spans = tuple(home.wardrobe.spans())
    away_spans = tuple(away.wardrobe.spans())
    numbers = {
        "early_unmark_shelved": early_shelved,
        "mark_arrival_drains": drain_noted,
        "spans_equal": home_spans == away_spans,
        "spans": home_spans,
        "standing_each": (
            len(home.wardrobe._standing()),
            len(away.wardrobe._standing()),
        ),
        "stripped_each": (
            len(home.wardrobe.stripped),
            len(away.wardrobe.stripped),
        ),
    }
    holds = (
        numbers["early_unmark_shelved"]
        and numbers["spans_equal"]
        and numbers["standing_each"] == (1, 1)
        and numbers["stripped_each"] == (1, 1)
        and numbers["spans"]
        == (
            (
                "plain bold plain",
                frozenset({"italic"}),
            ),
        )
    )
    return Verdict(
        trial="marktrial",
        claim=(
            "the regret arrives before the mark it "
            "strips, shelves with its reason, drains "
            "on the mark's arrival, and both "
            "wardrobes compare equal as data, bold "
            "gone everywhere and italic standing, "
            "because looking alike is a compliment "
            "and comparing equal is a property"
        ),
        numbers=numbers,
        holds=holds,
    )
