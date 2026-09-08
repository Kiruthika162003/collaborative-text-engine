from __future__ import annotations

from loom.author import Author
from loom.mentions import mentioned, mentions, page, unknown

ROSTER = {"alice", "bob", "cara"}


class TestFinding:
    def test_a_mention_is_found_and_resolved(self):
        author = Author(site="alice")
        author.type_at(0, "ping @bob about this")
        found = mentions(author.weave, ROSTER)
        assert len(found) == 1
        assert found[0].handle == "bob"
        assert found[0].known

    def test_a_bare_at_sign_is_not_a_mention(self):
        author = Author(site="alice")
        author.type_at(0, "email a@ b")
        assert mentions(author.weave, ROSTER) == []

    def test_a_handle_not_in_the_room_is_a_stranger(self):
        author = Author(site="alice")
        author.type_at(0, "hey @dave")
        found = mentions(author.weave, ROSTER)
        assert not found[0].known


class TestRollups:
    def test_mentioned_lists_only_the_known(self):
        author = Author(site="alice")
        author.type_at(0, "@alice and @dave and @bob")
        assert mentioned(author.weave, ROSTER) == {"alice", "bob"}

    def test_unknown_gathers_the_probable_typos(self):
        author = Author(site="alice")
        author.type_at(0, "@dave @erin")
        strangers = {m.handle for m in unknown(author.weave, ROSTER)}
        assert strangers == {"dave", "erin"}


class TestPin:
    def test_a_mention_pin_survives_upstream_edits(self):
        author = Author(site="alice")
        author.type_at(0, "see @cara here")
        pin = mentions(author.weave, ROSTER)[0].pin
        author.type_at(0, "PREFIX ")
        moved = mentions(author.weave, ROSTER)[0]
        assert moved.pin == pin
        assert moved.handle == "cara"

    def test_a_deleted_at_sign_drops_the_mention(self):
        author = Author(site="alice")
        author.type_at(0, "@bob")
        author.erase_at(0, 1)
        assert mentions(author.weave, ROSTER) == []


class TestPage:
    def test_the_page_separates_room_from_strangers(self):
        author = Author(site="alice")
        author.type_at(0, "@bob and @dave")
        rendered = page(author.weave, ROSTER)
        assert "in the room: bob" in rendered
        assert "probable typos): dave" in rendered

    def test_an_unmentioned_document_says_so(self):
        author = Author(site="alice")
        author.type_at(0, "plain prose")
        assert "nobody was named" in page(author.weave, ROSTER)
