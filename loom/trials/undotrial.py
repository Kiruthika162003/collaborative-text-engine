"""The undotrial: apologies crossing mischief, and the ledger balancing.

Two scribes type, cross-deliver through gremlin links,
and then one regrets: alice undoes her last gesture while
bob keeps typing into the very stretch she is unsaying.
The trial measures what a shared undo must guarantee and
what it must not pretend. Guaranteed and measured: the
circle converges after the apologies land, the undone
stretch is gone at every site, bob's concurrent typing
survives untouched because his strands were never hers to
unsay, and the redo brings her stretch back as fresh
strands with fresh ids, seven new operations rather than
seven ghosts. Not pretended: undo does not restore the
world, only her words, and the trial's final text carries
bob's interjection standing exactly where the fabric
seated it, which reads oddly and converges perfectly,
the standing order of this workshop being that odd and
identical beats pretty and divergent every time.
"""

from __future__ import annotations

from loom.circle import Circle
from loom.snapshot import fabric_digest
from loom.trials.verdict import Verdict
from loom.undo import Scribe


def run() -> Verdict:
    circle = Circle.of(
        ["alice", "bob"],
        temperament="gremlin",
        seed=17,
    )
    alice = Scribe(author=circle.author("alice"))
    bob = Scribe(author=circle.author("bob"))

    circle.say("alice", alice.type_at(0, "steady "))
    circle.settle()
    circle.say("alice", alice.type_at(7, "regret!"))
    circle.say("bob", bob.type_at(7, "[bob] "))
    circle.settle()
    before_undo = circle.converged()

    undo_ops = alice.undo()
    circle.say("alice", undo_ops)
    circle.settle()
    after_undo = circle.converged()

    redo_ops = alice.redo()
    circle.say("alice", redo_ops)
    circle.settle()
    after_redo = circle.converged()

    numbers = {
        "before_undo": before_undo,
        "after_undo": after_undo,
        "after_redo": after_redo,
        "undo_ops": len(undo_ops),
        "redo_ops": len(redo_ops),
        "regret_gone": "regret!" not in after_undo,
        "bob_survives": "[bob] " in after_undo,
        "redo_is_fresh": all(
            op.id.counter > 14 for op in redo_ops
        ),
        "one_fabric": fabric_digest(
            circle.author("alice").weave
        )
        == fabric_digest(circle.author("bob").weave),
    }
    holds = (
        numbers["regret_gone"]
        and numbers["bob_survives"]
        and numbers["one_fabric"]
        and numbers["undo_ops"] == 7
        and numbers["redo_ops"] == 7
        and numbers["redo_is_fresh"]
        and numbers["before_undo"]
        == "steady [bob] regret!"
        and numbers["after_undo"] == "steady [bob] "
        and numbers["after_redo"]
        == "steady [bob] regret!"
    )
    return Verdict(
        trial="undotrial",
        claim=(
            "the apology lands everywhere, the "
            "undone stretch is gone at every site, "
            "the concurrent hand survives untouched, "
            "and redo returns as seven fresh "
            "operations rather than seven ghosts; "
            "odd and identical beats pretty and "
            "divergent every time"
        ),
        numbers=numbers,
        holds=holds,
    )
