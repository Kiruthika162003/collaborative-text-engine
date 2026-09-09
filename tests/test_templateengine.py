from __future__ import annotations

from loom.templateengine import render


class TestVariables:
    def test_a_variable_is_substituted(self):
        assert render("Hi {{name}}", {"name": "Al"}) == "Hi Al"

    def test_a_missing_variable_is_empty(self):
        assert render("gap {{x}}", {}) == "gap "

    def test_a_dotted_path_walks_nested_dicts(self):
        assert render("{{user.name}}", {"user": {"name": "Al"}}) == "Al"


class TestConditionals:
    def test_a_truthy_if_renders(self):
        assert render("{{#if on}}yes{{/if}}", {"on": True}) == "yes"

    def test_a_falsy_if_is_empty(self):
        assert render("{{#if on}}yes{{/if}}", {"on": False}) == ""

    def test_an_empty_list_is_falsy(self):
        assert render("{{#if xs}}has{{/if}}", {"xs": []}) == ""


class TestLoops:
    def test_each_over_scalars_uses_dot(self):
        assert render("{{#each xs}}[{{.}}]{{/each}}", {"xs": ["a", "b"]}) == (
            "[a][b]"
        )

    def test_each_over_dicts_uses_keys(self):
        out = render(
            "{{#each rows}}{{name}} {{/each}}",
            {"rows": [{"name": "Al"}, {"name": "Bob"}]},
        )
        assert out == "Al Bob "

    def test_an_if_nested_in_each(self):
        out = render(
            "{{#each xs}}{{#if on}}{{v}}{{/if}}{{/each}}",
            {"xs": [{"on": True, "v": "a"}, {"on": False, "v": "b"}]},
        )
        assert out == "a"

    def test_the_outer_context_is_visible_in_a_loop(self):
        out = render(
            "{{#each xs}}{{prefix}}{{.}} {{/each}}",
            {"prefix": ">", "xs": ["a", "b"]},
        )
        assert out == ">a >b "
