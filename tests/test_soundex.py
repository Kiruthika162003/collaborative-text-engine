from __future__ import annotations

from loom.soundex import soundex, sounds_like


class TestSoundex:
    def test_classic_codes(self):
        assert soundex("Robert") == "R163"
        assert soundex("Tymczak") == "T522"
        assert soundex("Pfister") == "P236"
        assert soundex("Honeyman") == "H555"

    def test_the_hw_rule_merges_across(self):
        assert soundex("Ashcraft") == "A261"

    def test_the_code_is_four_characters(self):
        assert len(soundex("Lee")) == 4

    def test_a_wordless_input_is_empty(self):
        assert soundex("123") == ""


class TestSoundsLike:
    def test_names_that_sound_alike_match(self):
        assert sounds_like("Robert", "Rupert")

    def test_unrelated_names_do_not_match(self):
        assert not sounds_like("Robert", "Alice")

    def test_empty_never_sounds_like_anything(self):
        assert not sounds_like("", "")
