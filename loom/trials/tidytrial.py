"""The tidytrial: formatting one replica while another edits content loses neither.

Formatting is a large edit, and the fear is that running it
while a collaborator types would either lose their keystrokes
or diverge. This stages it: alice runs the full tidy pass on a
messy base, normalizing bullets and trimming trailing space,
while bob concurrently appends a distinctive word to the
content, and then the replicas exchange. Because every fixer
tidy runs is expressed through the patch that touches only
what differs, the strands carrying bob's content region are
untouched by alice's formatting, so bob's insertion anchors to
living strands and the two replicas converge to one fabric
with the formatting applied and bob's word present. The trial
measures all three: that tidy actually did work, a positive op
count, so the pass was not a no-op that would prove nothing;
that the replicas agree on one digest; and that bob's word
survived. The guess it refutes is that formatting and editing
cannot safely overlap, that a document must be locked while
tidied. It need not, because formatting through the patch is
surgical, and surgical edits and concurrent edits compose the
way every other pair of concurrent edits in this engine does.
"""

from __future__ import annotations

from loom.author import Author
from loom.snapshot import fabric_digest
from loom.tidy import tidy
from loom.trials.verdict import Verdict

MARK = "NOTE"


def run() -> Verdict:
    alice = Author(site="alice")
    bob = Author(site="bob")
    base = alice.type_at(0, "* item one  \n+ item two")
    for op in base:
        bob.absorb(op)

    tidy_ops = tidy(alice)
    bob_ops = bob.type_at(bob.weave.visible_count(), MARK)

    for op in tidy_ops:
        bob.absorb(op)
    for op in bob_ops:
        alice.absorb(op)

    digests = {fabric_digest(alice.weave), fabric_digest(bob.weave)}
    text = alice.text()
    numbers = {
        "tidy_ops": len(tidy_ops),
        "one_digest": len(digests) == 1,
        "mark_survived": MARK in text and MARK in bob.text(),
        "bullets_normalized": "* " not in text and "+ " not in text,
        "converged_text": text,
    }
    holds = (
        numbers["one_digest"]
        and numbers["mark_survived"]
        and numbers["bullets_normalized"]
        and numbers["tidy_ops"] > 0
    )
    return Verdict(
        trial="tidytrial",
        claim=(
            "running the full tidy pass on one replica while a "
            "collaborator edits content converges to one fabric "
            "with the formatting applied and the keystroke kept, "
            "because tidy formats through the patch and surgical "
            "edits compose with concurrent ones like any others; "
            "a document need not be locked while it is tidied"
        ),
        numbers=numbers,
        holds=holds,
    )
