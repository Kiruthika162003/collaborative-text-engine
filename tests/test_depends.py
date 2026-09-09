from __future__ import annotations

from loom.author import Author
from loom.depends import dependencies, missing, ready
from loom.ids import OpId


def run() -> list:
    author = Author(site="alice")
    return author.type_at(0, "ab")


class TestDependencies:
    def test_the_first_insert_depends_on_nothing(self):
        ops = run()
        assert dependencies(ops[0]) == set()

    def test_a_later_insert_depends_on_predecessor_and_origin(self):
        ops = run()
        # second glyph: predecessor (alice,1) and origin (alice,1) coincide
        assert dependencies(ops[1]) == {ops[0].id}

    def test_a_shear_depends_on_its_target_and_predecessor(self):
        author = Author(site="alice")
        typed = author.type_at(0, "xy")
        shear = author.erase_at(0, 1)[0]
        deps = dependencies(shear)
        assert typed[0].id in deps
        assert OpId("alice", shear.id.counter - 1) in deps


class TestReadiness:
    def test_an_op_with_all_deps_is_ready(self):
        ops = run()
        assert ready(ops[1], {ops[0].id})

    def test_an_op_missing_a_dep_is_not_ready(self):
        ops = run()
        assert not ready(ops[1], set())

    def test_missing_names_the_absent_deps(self):
        ops = run()
        assert missing(ops[1], set()) == {ops[0].id}
        assert missing(ops[1], {ops[0].id}) == set()


class TestModel:
    def test_a_head_origin_is_not_a_dependency(self):
        ops = run()
        # first insert's origin is HEAD, so it contributes no dep
        assert ops[0].id not in dependencies(ops[0])
