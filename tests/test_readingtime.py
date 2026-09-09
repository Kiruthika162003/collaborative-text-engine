from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Invalid
from loom.readingtime import reading_minutes, reading_time


def words(count: int) -> Author:
    author = Author(site="alice")
    author.type_at(0, "word " * count)
    return author


class TestMinutes:
    def test_two_hundred_words_at_two_hundred_wpm_is_one_minute(self):
        assert reading_minutes(words(200)) == 1.0

    def test_a_custom_speed_is_used(self):
        assert reading_minutes(words(300), wpm=100) == 3.0

    def test_a_non_positive_speed_is_refused(self):
        with pytest.raises(Invalid):
            reading_minutes(words(10), wpm=0)


class TestTime:
    def test_a_full_minute_rounds(self):
        assert reading_time(words(400)) == "about 2 min"

    def test_a_short_read_is_under_a_minute(self):
        assert reading_time(words(50)) == "under a minute"

    def test_an_empty_document_has_nothing_to_read(self):
        author = Author(site="alice")
        assert reading_time(author) == "nothing to read"
