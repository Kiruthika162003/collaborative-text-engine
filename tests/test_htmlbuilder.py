from __future__ import annotations

from loom.htmlbuilder import element


class TestRender:
    def test_a_simple_element(self):
        assert element("p").add("hello").render() == "<p>hello</p>"

    def test_text_children_are_escaped(self):
        assert element("p").add("a<b").render() == "<p>a&lt;b</p>"

    def test_attributes_render(self):
        out = element("a", href="http://x").add("link").render()
        assert out == '<a href="http://x">link</a>'

    def test_attribute_values_are_escaped(self):
        out = element("span").attr("title", 'a"b').render()
        assert out == '<span title="a&quot;b"></span>'

    def test_nested_elements(self):
        out = element("div").add(element("span").add("x")).render()
        assert out == "<div><span>x</span></div>"


class TestVoid:
    def test_a_void_element_self_closes(self):
        assert element("br").render() == "<br>"

    def test_a_void_element_ignores_children(self):
        assert element("img", src="a.png").add("ignored").render() == (
            '<img src="a.png">'
        )
