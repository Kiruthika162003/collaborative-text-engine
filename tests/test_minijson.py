from __future__ import annotations

import pytest

from loom.errors import Invalid, Torn
from loom.minijson import decode, encode


class TestEncode:
    def test_scalars(self):
        assert encode(None) == "null"
        assert encode(True) == "true"
        assert encode(42) == "42"

    def test_a_string_is_escaped(self):
        assert encode('a"b\n') == '"a\\"b\\n"'

    def test_a_nested_structure(self):
        assert encode({"a": [1, 2]}) == '{"a":[1,2]}'

    def test_an_unencodable_type_is_refused(self):
        with pytest.raises(Invalid):
            encode({1, 2})


class TestDecode:
    def test_scalars(self):
        assert decode("null") is None
        assert decode("true") is True
        assert decode("42") == 42
        assert decode("3.5") == 3.5

    def test_a_string_with_escapes(self):
        assert decode('"a\\"b\\n"') == 'a"b\n'

    def test_a_unicode_escape(self):
        assert decode('"\\u0041"') == "A"

    def test_an_object_and_array(self):
        assert decode('{"a": [1, 2], "b": null}') == {"a": [1, 2], "b": None}

    def test_trailing_content_is_refused(self):
        with pytest.raises(Torn):
            decode("1 2")

    def test_an_unterminated_string_is_refused(self):
        with pytest.raises(Torn):
            decode('"open')


class TestRoundTrip:
    def test_encode_then_decode_is_identity(self):
        for value in [
            None,
            True,
            42,
            3.14,
            "hi",
            [1, "a", None],
            {"x": [True, {"y": 2}]},
        ]:
            assert decode(encode(value)) == value
