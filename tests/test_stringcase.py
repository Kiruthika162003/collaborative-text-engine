from __future__ import annotations

from loom.stringcase import (
    detect,
    to_camel,
    to_constant,
    to_kebab,
    to_pascal,
    to_snake,
    words,
)


class TestWords:
    def test_snake_splits_on_underscore(self):
        assert words("hello_world") == ["hello", "world"]

    def test_camel_splits_on_case(self):
        assert words("helloWorld") == ["hello", "world"]

    def test_an_acronym_run_splits_correctly(self):
        assert words("HTTPServer") == ["http", "server"]

    def test_kebab_and_spaces_split(self):
        assert words("a-b c") == ["a", "b", "c"]


class TestConversions:
    def test_to_snake(self):
        assert to_snake("helloWorld") == "hello_world"

    def test_to_kebab(self):
        assert to_kebab("HelloWorld") == "hello-world"

    def test_to_constant(self):
        assert to_constant("helloWorld") == "HELLO_WORLD"

    def test_to_camel(self):
        assert to_camel("hello_world") == "helloWorld"

    def test_to_pascal(self):
        assert to_pascal("hello-world") == "HelloWorld"


class TestDetect:
    def test_styles_are_named(self):
        assert detect("hello_world") == "snake"
        assert detect("hello-world") == "kebab"
        assert detect("HELLO_WORLD") == "constant"
        assert detect("HelloWorld") == "pascal"
        assert detect("helloWorld") == "camel"

    def test_a_single_word_is_flat(self):
        assert detect("hello") == "flat"
