from __future__ import annotations

import pytest

from loom.changelog import Changelog
from loom.errors import Invalid


class TestBuild:
    def test_a_version_and_entries_render(self):
        out = (
            Changelog()
            .version("1.0", "2020-01-01")
            .added("a feature")
            .fixed("a bug")
            .render()
        )
        assert "## 1.0 - 2020-01-01" in out
        assert "### Added\n- a feature" in out
        assert "### Fixed\n- a bug" in out

    def test_categories_render_in_canonical_order(self):
        out = (
            Changelog()
            .version("1.0")
            .fixed("bug")
            .added("feature")
            .render()
        )
        assert out.index("### Added") < out.index("### Fixed")

    def test_an_unused_category_is_omitted(self):
        out = Changelog().version("1.0").added("x").render()
        assert "### Fixed" not in out


class TestGuards:
    def test_adding_before_a_version_is_refused(self):
        with pytest.raises(Invalid):
            Changelog().added("orphan")

    def test_a_dateless_version_omits_the_date(self):
        out = Changelog().version("2.0").added("x").render()
        assert "## 2.0" in out
        assert "## 2.0 -" not in out


class TestHeader:
    def test_the_document_opens_with_a_changelog_heading(self):
        assert Changelog().render() == "# Changelog"
