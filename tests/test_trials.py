from __future__ import annotations

from loom.cli import main
from loom.trials import registry
from loom.trials.duet import run as duet_run


class TestTheDuet:
    def test_the_verdict_holds(self):
        verdict = duet_run()
        assert verdict.holds

    def test_the_brown_fox_stands(self):
        verdict = duet_run()
        assert verdict.numbers["alice_text"] == (
            "the brown fox"
        )
        assert verdict.numbers["converged"]

    def test_bobs_rank_reflects_what_he_witnessed(self):
        verdict = duet_run()
        assert verdict.numbers["bob_first_rank"] == 14

    def test_reversed_delivery_shelves_all_but_one(self):
        verdict = duet_run()
        assert verdict.numbers["shelved_at_bob"] == 5
        assert verdict.numbers["shelved_at_alice"] == 5


class TestTheDocket:
    def test_no_trial_is_broken(self):
        assert registry.broken() == []
        assert "0 broken" in registry.docket()


class TestTheCli:
    def test_summary_speaks_one_line(self, capsys):
        assert main(["summary"]) == 0
        out = capsys.readouterr().out
        assert out.strip().endswith("trials (0 broken)")

    def test_check_is_quietly_green(self, capsys):
        assert main(["check"]) == 0
        assert "every trial holds" in (
            capsys.readouterr().out
        )

    def test_one_trial_prints_its_numbers(self, capsys):
        assert main(["trial", "duet"]) == 0
        out = capsys.readouterr().out
        assert out.startswith("duet: holds")
        assert "alice_text = the brown fox" in out

    def test_a_stranger_gets_the_docket(self, capsys):
        assert main(["trial", "ghost"]) == 2
        out = capsys.readouterr().out
        assert "not on the docket" in out
        assert "duet" in out

    def test_no_command_prints_help(self, capsys):
        assert main([]) == 2
        assert "usage" in capsys.readouterr().out
