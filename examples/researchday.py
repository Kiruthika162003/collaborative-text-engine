"""A research day: two hands draft a note, cite a source, and read the result.

Alice lays down a heading and the body, bob appends a line
and cites a source into a shared bibliography, and the day
closes with the reading organs that never existed until the
document did: the outline off the headings, the works-cited
off the citations, the sentence count, the readability
arithmetic that grades length not thought, the page split,
and the dashboard reading the session's rhythm and balance.
Every operation is recorded once to a shared session tape in
the order it happened, and both weaves converge, so the
dashboard reads a genuine two-hand session. Run with:
python -m examples.researchday
"""

from __future__ import annotations

from loom.author import Author
from loom.citations import Bibliography, Citation, Citations, Source
from loom.dashboard import page as dashboard_page
from loom.headings import outline
from loom.ids import OpId
from loom.pages import page_count
from loom.readability import flesch_reading_ease
from loom.sentences import sentence_count
from loom.transcript import Tape


def main() -> int:
    tape = Tape()
    alice = Author(site="alice")
    bob = Author(site="bob")

    def sync(source: Author, ops: list) -> None:
        for op in ops:
            tape.record(op)
        other = bob if source is alice else alice
        for op in ops:
            other.absorb(op)

    sync(
        alice,
        alice.type_at(
            0,
            "# Field Notes\nThe river rose fast. "
            "We moved camp uphill. Nobody was hurt.",
        ),
    )
    sync(
        bob,
        bob.type_at(bob.weave.visible_count(), " Rain fell all night."),
    )
    print(f"text:    {alice.text()!r}")

    print()
    print("outline:")
    print(outline(alice.weave))

    biblio = Bibliography()
    biblio.enter(
        Source(
            key="rees",
            author="Rees, M",
            title="Flood Watch",
            year=2018,
        )
    )
    marks = Citations(weave=alice.weave, bibliography=biblio)
    rain = alice.weave.visible_count() - len(" Rain fell all night.") + 1
    marks.cite(Citation(OpId("alice", 500), alice.weave.strand_at_visible(rain).id, "rees"))
    print()
    print("works cited:")
    print(marks.works_cited())

    print()
    print(f"sentences: {sentence_count(alice.weave)}")
    print(f"ease:      {flesch_reading_ease(alice.weave)}")
    print(f"pages:     {page_count(alice.weave, 1)} at one line each")

    print()
    print(dashboard_page(alice.weave, tape))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
