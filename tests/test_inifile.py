from __future__ import annotations

from loom.inifile import get, parse, render


class TestParse:
    def test_sections_and_keys(self):
        config = parse("[db]\nhost = localhost\nport = 5432\n\n[web]\nport = 80")
        assert config == {
            "db": {"host": "localhost", "port": "5432"},
            "web": {"port": "80"},
        }

    def test_default_section_keys_before_any_header(self):
        config = parse("name = top\n[s]\nk = v")
        assert config[""] == {"name": "top"}
        assert config["s"] == {"k": "v"}

    def test_comments_are_skipped(self):
        config = parse("; a comment\n# another\n[s]\nk = v")
        assert config == {"s": {"k": "v"}}

    def test_a_duplicate_key_takes_the_last(self):
        config = parse("[s]\nk = one\nk = two")
        assert config["s"]["k"] == "two"


class TestRender:
    def test_render_round_trips(self):
        config = {"db": {"host": "x", "port": "1"}, "web": {"port": "80"}}
        assert parse(render(config)) == config

    def test_the_default_section_renders_at_the_top(self):
        config = {"": {"name": "top"}, "s": {"k": "v"}}
        out = render(config)
        assert out.startswith("name = top")


class TestGet:
    def test_get_reads_a_value(self):
        config = parse("[s]\nk = v")
        assert get(config, "s", "k") == "v"

    def test_get_returns_a_default(self):
        assert get({}, "s", "missing", "fallback") == "fallback"
