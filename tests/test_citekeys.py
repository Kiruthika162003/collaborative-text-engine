from __future__ import annotations

from loom.citations import Source
from loom.citekeys import assign_keys, make_key


class TestMakeKey:
    def test_surname_and_year(self):
        assert make_key(Source("x", "Smith, J", "T", 2020)) == "smith2020"

    def test_a_yearless_source_uses_nd(self):
        assert make_key(Source("x", "Smith, J", "T")) == "smithnd"

    def test_a_first_word_surname_when_no_comma(self):
        assert make_key(Source("x", "Smith", "T", 2019)) == "smith2019"

    def test_an_authorless_source_is_anon(self):
        assert make_key(Source("x", "", "Titled", 2000)) == "anon2000"


class TestAssignKeys:
    def test_a_lone_key_is_unsuffixed(self):
        sources = [Source("x", "Smith, J", "One", 2020)]
        assert assign_keys(sources) == [(sources[0], "smith2020")]

    def test_collisions_get_letter_suffixes(self):
        sources = [
            Source("x", "Smith, J", "One", 2020),
            Source("y", "Smith, K", "Two", 2020),
        ]
        keys = [key for _source, key in assign_keys(sources)]
        assert keys == ["smith2020a", "smith2020b"]

    def test_distinct_sources_keep_plain_keys(self):
        sources = [
            Source("x", "Smith, J", "One", 2020),
            Source("y", "Jones, K", "Two", 2019),
        ]
        keys = [key for _source, key in assign_keys(sources)]
        assert keys == ["smith2020", "jones2019"]
