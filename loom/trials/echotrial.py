"""The echotrial: the mailroom recognizes a repeat by the clock, so resending is safe.

Anti-entropy resends operations it is not sure the other side
received, so the whole scheme rests on redelivery being harmless.
This stages exactly that. Alice types a sentence and erases a word
from it, and two mailrooms hear the resulting operations: charlie
hears each one once, the clean network, while bob hears the whole
stream and then hears the entire stream a second time, the network
that duplicates. If redelivery were not caught the two would part
ways, but they do not; bob's fabric ends identical to charlie's and
to alice's, and bob's mailroom counts exactly one repeat for every
operation in the second pass. I had first guessed the weave itself
made redelivery harmless, that asking it to weave the same insert
twice would simply weave it once and asking it to shear an
already-cut strand would leave the tombstone as it was, so nothing
above the weave needed to guard against repeats. Half of that is
true, the weave is idempotent, but the author's absorb path is not
asked so gently: it observes each operation on the version vector,
and the vector refuses a counter it has already recorded as stale
rather than shrugging it off, so handing the same operation to
absorb twice raises, it does not no-op. The guard therefore cannot
live in the weave being asked twice; it has to live one layer up,
in the mailroom, which asks the clock whether it has already seen
an operation before offering it to absorb at all and returns a
repeat as an already-woven receipt when it has. So the honest
location of idempotence is the mailroom's clock check, not the
weave's tolerance, and that is what this pins down: a listener fed
the stream twice through its mailroom converges to the same fabric
as one fed it once, at-least-once delivery matching exactly-once,
because the mailroom drops what the clock says it already holds.
"""

from __future__ import annotations

from loom.author import Author
from loom.mailroom import Mailroom
from loom.snapshot import fabric_digest
from loom.trials.verdict import Verdict


def run() -> Verdict:
    alice = Author(site="alice")
    typed = alice.type_at(0, "the quick brown fox")
    sheared = alice.erase_at(4, 6)
    stream = typed + sheared

    bob = Mailroom(author=Author(site="bob"))
    charlie = Mailroom(author=Author(site="charlie"))

    for op in stream:
        charlie.receive(op)
    for op in stream:
        bob.receive(op)
    for op in stream:
        bob.receive(op)

    digests = {
        fabric_digest(alice.weave),
        fabric_digest(bob.author.weave),
        fabric_digest(charlie.author.weave),
    }
    numbers = {
        "deliveries_to_bob": 2 * len(stream),
        "unique_ops": len(stream),
        "bob_woven": bob.woven,
        "bob_duplicates": bob.duplicates,
        "one_digest": len(digests) == 1,
        "bob_matches_single_delivery": bob.author.text() == charlie.author.text(),
        "converged_text": bob.author.text(),
    }
    holds = (
        numbers["one_digest"]
        and numbers["bob_matches_single_delivery"]
        and numbers["bob_woven"] == numbers["unique_ops"]
        and numbers["bob_duplicates"] == numbers["unique_ops"]
    )
    return Verdict(
        trial="echotrial",
        claim=(
            "the mailroom asks the clock whether it has already "
            "seen an operation and drops the repeat, since the "
            "version vector treats a re-observed counter as stale "
            "rather than a no-op; a listener fed the whole stream "
            "twice through its mailroom converges to the same "
            "fabric as one fed it once, so at-least-once delivery "
            "matches exactly-once and anti-entropy can resend"
        ),
        numbers=numbers,
        holds=holds,
    )
