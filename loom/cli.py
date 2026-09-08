"""The command line: the docket read aloud, nothing paraphrased."""

from __future__ import annotations

import argparse
import importlib
import sys


def _trial_names() -> list[str]:
    from loom.trials import registry

    return [
        dotted.rsplit(".", 1)[-1]
        for dotted in registry.TRIALS
    ]


def _run_summary() -> int:
    from loom.trials import registry

    verdicts = registry.all_verdicts()
    failing = sum(
        1 for held in verdicts if not held.holds
    )
    print(f"{len(verdicts)} trials ({failing} broken)")
    return 1 if failing else 0


def _run_check() -> int:
    from loom.trials import registry

    failing = registry.broken()
    if failing:
        print(
            f"{len(failing)} trial(s) broken: "
            + ", ".join(failing)
        )
        return 1
    print("every trial holds")
    return 0


def _run_docket() -> int:
    from loom.trials import registry

    print(registry.docket())
    return 0


def _run_trial(name: str) -> int:
    names = _trial_names()
    if name not in names:
        print(
            f"{name} is not on the docket; the "
            "docket: " + ", ".join(names)
        )
        return 2
    module = importlib.import_module(
        f"loom.trials.{name}"
    )
    verdict = module.run()
    print(verdict.page())
    return 0 if verdict.holds else 1


def _run_rooms() -> int:
    from loom.rooms import directory

    print(directory())
    return 0


def _run_days() -> int:
    from loom.rooms import itinerary

    print(itinerary())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="loom")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser(
        "summary", help="one line: N trials (M broken)"
    )
    commands.add_parser(
        "rooms",
        help="every module and its first sentence",
    )
    commands.add_parser(
        "days",
        help="every example and its first sentence",
    )
    commands.add_parser(
        "check",
        help="exit nonzero if any trial is broken",
    )
    commands.add_parser(
        "docket", help="every verdict, one page"
    )
    trial_parser = commands.add_parser(
        "trial", help="one verdict with its numbers"
    )
    trial_parser.add_argument("name")
    arguments = parser.parse_args(argv)
    if arguments.command == "summary":
        return _run_summary()
    if arguments.command == "check":
        return _run_check()
    if arguments.command == "docket":
        return _run_docket()
    if arguments.command == "trial":
        return _run_trial(arguments.name)
    if arguments.command == "rooms":
        return _run_rooms()
    if arguments.command == "days":
        return _run_days()
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
