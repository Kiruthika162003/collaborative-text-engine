from __future__ import annotations

from loom.author import Author
from loom.autosave import Autosave


def watched() -> tuple[Author, Autosave]:
    author = Author(site="alice")
    return author, Autosave(weave=author.weave)


class TestDirtyLine:
    def test_a_fresh_document_is_clean(self):
        _author, save = watched()
        assert not save.is_dirty()

    def test_typing_makes_it_dirty(self):
        author, save = watched()
        author.type_at(0, "hi")
        assert save.is_dirty()

    def test_undo_to_saved_state_is_clean_again(self):
        author, save = watched()
        author.type_at(0, "temp")
        save.save(1)
        author.erase_at(0, 4)
        save.save(2)
        author.type_at(0, "temp")
        author.erase_at(0, 4)
        assert not save.is_dirty()


class TestTriggers:
    def test_the_quiet_interval_fires(self):
        author, save = watched()
        author.type_at(0, "burst")
        save.touched(10)
        assert not save.should_save(12)
        assert save.should_save(15)

    def test_the_hard_cap_fires_under_constant_typing(
        self,
    ):
        author, save = watched()
        author.type_at(0, "x")
        save.touched(1)
        for tick in range(2, 40):
            author.type_at(0, "y")
            save.touched(tick)
        assert save.should_save(35)

    def test_a_clean_document_never_saves(self):
        _author, save = watched()
        assert not save.should_save(999)
        assert save.tick(999) == "no save needed"


class TestSaving:
    def test_saving_updates_the_truth(self):
        author, save = watched()
        author.type_at(0, "content")
        receipt = save.save(5)
        assert "saved at tick 5" in receipt
        assert not save.is_dirty()
        assert save.saves == 1

    def test_tick_names_the_reason(self):
        author, save = watched()
        author.type_at(0, "burst")
        save.touched(10)
        assert "quiet interval" in save.tick(20)
