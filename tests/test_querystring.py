from __future__ import annotations

from loom.querystring import encode, parse, quote, unquote


class TestQuote:
    def test_unsafe_characters_are_encoded(self):
        assert quote("a b&c") == "a+b%26c"

    def test_unquote_reverses(self):
        assert unquote("a+b%26c") == "a b&c"

    def test_utf8_round_trips(self):
        assert unquote(quote("café")) == "café"


class TestParse:
    def test_pairs_parse_to_lists(self):
        assert parse("a=1&b=2") == {"a": ["1"], "b": ["2"]}

    def test_a_repeated_key_collects_values(self):
        assert parse("a=1&a=2") == {"a": ["1", "2"]}

    def test_an_encoded_value_is_decoded(self):
        assert parse("q=hello+world") == {"q": ["hello world"]}

    def test_an_empty_query_is_empty(self):
        assert parse("") == {}


class TestEncode:
    def test_a_scalar_and_a_list(self):
        assert encode({"q": "hi there", "t": ["a", "b"]}) == (
            "q=hi+there&t=a&t=b"
        )

    def test_round_trip(self):
        params = {"a": ["1", "2"], "b": ["x y"]}
        assert parse(encode(params)) == params
