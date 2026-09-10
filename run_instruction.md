# Running collaborative-text-engine

A collaborative text editing engine built on a replicated growable array text
CRDT, written in Python. This file covers how to build the project, run its
tests, and execute it. Every command below was run from a clean checkout of this
repository before being written down.

## Requirements

Python 3.11 or newer. There are no third party runtime dependencies.

## Setup

Nothing to install. The package has no dependencies, so every command below runs
from the repository root against the source tree as it stands.

## Run the tests

```bash
python -m pytest -q
```

The suite is the primary check. It runs from the repository root with no
arguments and no configuration, and it prints the number of tests it ran. A
non-zero exit status means something is wrong. Read the printed summary rather
than a shell pipeline, because piping the output through another command
replaces the real exit code with that of the last command in the pipe.

## Lint

```bash
python -m ruff check .
```

The lint configuration lives in `pyproject.toml`. It passes with no findings.

## Run the command line tool

```bash
python -m loom.cli --help
```

The subcommands are `summary`, `rooms`, `days`, `check`, `docket`, and `trial`.

`summary` prints one line giving the number of trials and how many are broken:

```bash
python -m loom.cli summary
```

`check` exits non-zero if any trial is broken, which makes it usable as a build
gate. `rooms` lists every module with its first sentence, `days` does the same
for the examples, `docket` prints every verdict, and `trial` prints one verdict
with its numbers.

At the time of writing `summary` reports `18 trials (0 broken)` and `check`
exits zero.

## Run a worked example

There are 9 runnable examples in `examples/`. Each exposes `run()`, which
returns the lines it would print, and `main()`, which prints them:

```bash
python -c "from examples.writingday import main; main()"
```

The full list is `analyticsday`, `collabnight`, `exportday`, `formatday`,
`pairday`, `researchday`, `reviewday`, `trainday`, and `writingday`.

## Layout

- `loom/` the package itself, 290 modules
- `loom/trials/` the verification organ, a set of measured claims about the
  package as a whole rather than unit tests of one function
- `tests/` the test suite, 303 files
- `examples/` runnable end to end scenarios

## Notes

The core of the package is the CRDT: a weave of characters with stable
identifiers, tombstones for deletions, and a merge that converges regardless of
the order operations arrive in. Around it sit the mailroom that routes
operations between sites, the handshake that brings a new site up to date, marks
for formatting that survive concurrent edits, and undo that respects other
people's work.

A number of general algorithms and data structures also live in `loom` and are
not part of the CRDT: string search and compression routines that the editor
uses, alongside sorting, graph, and numeric utilities that it does not. They are
self contained and tested on their own terms.

This repository has no README. The engine is complete and its tests pass, but
the closing summary was never written.
