from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.semver import Version, compare, parse, sort_versions


class TestParse:
    def test_a_core_version(self):
        assert parse("1.2.3") == Version(1, 2, 3, (), "")

    def test_prerelease_and_build(self):
        version = parse("1.0.0-alpha.1+build.5")
        assert version.prerelease == ("alpha", "1")
        assert version.build == "build.5"

    def test_a_bad_version_is_refused(self):
        with pytest.raises(Invalid):
            parse("1.0")


class TestCompare:
    def test_numeric_core_compares_as_numbers(self):
        assert compare("1.0.0", "2.0.0") == -1
        assert compare("1.10.0", "1.9.0") == 1

    def test_a_prerelease_is_below_the_release(self):
        assert compare("1.0.0-alpha", "1.0.0") == -1

    def test_prerelease_identifiers_compare(self):
        assert compare("1.0.0-alpha", "1.0.0-beta") == -1
        assert compare("1.0.0-alpha.1", "1.0.0-alpha.2") == -1

    def test_numeric_identifiers_rank_below_alphanumeric(self):
        assert compare("1.0.0-1", "1.0.0-alpha") == -1

    def test_more_identifiers_outrank_a_prefix(self):
        assert compare("1.0.0-alpha", "1.0.0-alpha.1") == -1

    def test_build_metadata_is_ignored(self):
        assert compare("1.0.0+a", "1.0.0+b") == 0


class TestSort:
    def test_versions_sort_by_precedence(self):
        versions = ["1.0.0", "1.0.0-alpha", "2.0.0", "1.0.0-beta"]
        assert sort_versions(versions) == [
            "1.0.0-alpha",
            "1.0.0-beta",
            "1.0.0",
            "2.0.0",
        ]
