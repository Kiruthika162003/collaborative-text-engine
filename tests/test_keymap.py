from __future__ import annotations

import pytest

from loom.errors import Diverged, Invalid
from loom.keymap import Keymap, normalize


class TestNormalize:
    def test_modifier_order_is_canonical(self):
        assert normalize("shift+ctrl+b") == "ctrl+shift+b"

    def test_aliases_and_case_are_folded(self):
        assert normalize("Control+B") == "ctrl+b"
        assert normalize("cmd+s") == normalize("command+s")

    def test_duplicate_modifiers_collapse(self):
        assert normalize("ctrl+ctrl+b") == "ctrl+b"

    def test_a_chord_without_a_key_is_refused(self):
        with pytest.raises(Invalid):
            normalize("ctrl+shift")

    def test_a_chord_with_two_keys_is_refused(self):
        with pytest.raises(Invalid):
            normalize("ctrl+a+b")


class TestBind:
    def test_a_binding_resolves_regardless_of_order(self):
        keys = Keymap()
        keys.bind("ctrl+shift+b", "bold")
        assert keys.resolve("shift+ctrl+b") == "bold"

    def test_rebinding_the_same_command_is_idempotent(self):
        keys = Keymap()
        keys.bind("ctrl+b", "bold")
        keys.bind("ctrl+b", "bold")
        assert len(keys.bindings) == 1

    def test_a_conflicting_bind_is_refused(self):
        keys = Keymap()
        keys.bind("ctrl+b", "bold")
        with pytest.raises(Diverged):
            keys.bind("ctrl+b", "italic")

    def test_rebind_overrides_on_purpose(self):
        keys = Keymap()
        keys.bind("ctrl+b", "bold")
        keys.rebind("ctrl+b", "italic")
        assert keys.resolve("ctrl+b") == "italic"

    def test_an_unbound_chord_resolves_to_nothing(self):
        assert Keymap().resolve("ctrl+q") is None

    def test_unbind_removes_a_binding(self):
        keys = Keymap()
        keys.bind("ctrl+b", "bold")
        assert keys.unbind("ctrl+b")
        assert keys.resolve("ctrl+b") is None


class TestMerge:
    def test_merging_unions_disjoint_bindings(self):
        left = Keymap()
        left.bind("ctrl+b", "bold")
        right = Keymap()
        right.bind("ctrl+i", "italic")
        merged = left.merge(right)
        assert merged.resolve("ctrl+b") == "bold"
        assert merged.resolve("ctrl+i") == "italic"

    def test_a_merge_conflict_is_raised(self):
        left = Keymap()
        left.bind("ctrl+b", "bold")
        right = Keymap()
        right.bind("ctrl+b", "brave")
        with pytest.raises(Diverged):
            left.merge(right)


class TestCheatSheet:
    def test_the_sheet_lists_bindings_in_order(self):
        keys = Keymap()
        keys.bind("ctrl+b", "bold", "make bold")
        keys.bind("ctrl+i", "italic")
        sheet = keys.cheat_sheet()
        assert "ctrl+b: bold  (make bold)" in sheet
        assert "ctrl+i: italic" in sheet

    def test_an_empty_keymap_says_so(self):
        assert "keymap is empty" in Keymap().cheat_sheet()
