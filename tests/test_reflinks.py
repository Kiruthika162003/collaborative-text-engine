from __future__ import annotations

from loom.reflinks import definitions, references, report, undefined, unused


class TestDefinitions:
    def test_a_definition_is_read(self):
        assert definitions("[home]: http://x") == {"home": "http://x"}

    def test_labels_fold_case(self):
        assert "home" in definitions("[Home]: http://x")


class TestReferences:
    def test_a_full_reference_is_read(self):
        assert references("see [the site][home] now") == [
            ("the site", "home")
        ]

    def test_a_collapsed_reference_uses_its_text(self):
        assert references("[home][]") == [("home", "home")]


class TestResolution:
    def test_a_defined_reference_is_not_undefined(self):
        text = "see [the site][home]\n\n[home]: http://x"
        assert undefined(text) == []

    def test_an_undefined_reference_is_flagged(self):
        assert undefined("see [x][ghost] here") == ["ghost"]

    def test_an_unused_definition_is_flagged(self):
        assert unused("[a]: http://u\ntext with no use") == ["a"]

    def test_a_used_definition_is_not_unused(self):
        text = "[t][a]\n\n[a]: http://u"
        assert unused(text) == []


class TestReport:
    def test_the_report_counts_and_flags(self):
        text = "[t][ghost]\n\n[a]: http://u"
        page = report(text)
        assert "1 reference(s), 1 definition(s)" in page
        assert "undefined: ghost" in page
        assert "unused definitions: a" in page

    def test_a_plain_document_has_nothing_to_resolve(self):
        assert "nothing to resolve" in report("just prose")
