from __future__ import annotations

from loom.pathutil import basename, dirname, join, normalize, split_ext


class TestJoin:
    def test_parts_join_with_one_slash(self):
        assert join("a", "b", "c") == "a/b/c"

    def test_an_absolute_part_resets(self):
        assert join("a", "/b") == "/b"

    def test_a_trailing_slash_is_not_doubled(self):
        assert join("a/", "b") == "a/b"


class TestNormalize:
    def test_dot_and_dotdot_resolve(self):
        assert normalize("a/./b/../c") == "a/c"

    def test_dotdot_at_root_stays(self):
        assert normalize("/a/../..") == "/"

    def test_a_relative_dotdot_is_kept(self):
        assert normalize("../a") == "../a"

    def test_a_bare_dotdot_collapses_to_dot(self):
        assert normalize("a/..") == "."


class TestSplit:
    def test_dirname_and_basename(self):
        assert dirname("/a/b/c") == "/a/b"
        assert basename("/a/b/c") == "c"

    def test_dirname_at_root(self):
        assert dirname("/a") == "/"

    def test_split_ext(self):
        assert split_ext("file.txt") == ("file", ".txt")
        assert split_ext("/a/b.tar") == ("/a/b", ".tar")

    def test_a_dotfile_has_no_extension(self):
        assert split_ext(".bashrc") == (".bashrc", "")

    def test_no_extension(self):
        assert split_ext("file") == ("file", "")
