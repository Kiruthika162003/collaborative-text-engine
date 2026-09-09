from __future__ import annotations

from loom.author import Author
from loom.fmvalidate import is_valid, validate


def doc(front: str) -> Author:
    author = Author(site="alice")
    author.type_at(0, front)
    return author


class TestRequired:
    def test_a_missing_required_field_is_flagged(self):
        author = doc("---\ntitle: T\n---\nbody")
        problems = validate(author.weave, required=frozenset({"title", "date"}))
        assert any("date" in p for p in problems)

    def test_all_required_present_is_clean(self):
        author = doc("---\ntitle: T\ndate: 2020-01-01\n---\nbody")
        assert validate(author.weave, required=frozenset({"title", "date"})) == []


class TestTypes:
    def test_an_int_field_is_checked(self):
        author = doc("---\ncount: five\n---\nbody")
        problems = validate(author.weave, types={"count": "int"})
        assert any("count" in p for p in problems)

    def test_a_good_int_passes(self):
        author = doc("---\ncount: 5\n---\nbody")
        assert validate(author.weave, types={"count": "int"}) == []

    def test_a_date_type_wants_iso(self):
        author = doc("---\nwhen: last tuesday\n---\nbody")
        assert validate(author.weave, types={"when": "date"}) != []

    def test_a_bool_type_accepts_yes(self):
        author = doc("---\ndraft: yes\n---\nbody")
        assert validate(author.weave, types={"draft": "bool"}) == []

    def test_an_unknown_type_is_not_validated(self):
        author = doc("---\nx: anything\n---\nbody")
        assert validate(author.weave, types={"x": "mystery"}) == []


class TestIsValid:
    def test_is_valid_gates_on_problems(self):
        author = doc("---\ntitle: T\n---\nbody")
        assert is_valid(author.weave, required=frozenset({"title"}))
        assert not is_valid(author.weave, required=frozenset({"missing"}))

    def test_a_document_without_front_matter_fails_required(self):
        author = doc("no front matter")
        assert not is_valid(author.weave, required=frozenset({"title"}))
