"""Regexlite: a small regex engine that runs every branch at once, never backtracking.

This matches a pattern of literals, the wildcard dot, star, plus,
question mark, alternation with the bar, and grouping with
parentheses, against a text, and it does so by Thompson's
construction rather than by the backtracking most hand-written
matchers use. The pattern is first parsed into a tree by recursive
descent, alternation over concatenation over repetition over
atoms, and the tree is compiled into a tiny program of
instructions: match a specific character, match any character,
succeed, jump, or split into two directions at once. Matching then
runs that program over the text as a set of live positions. Every
character of the text advances every live position by one step,
each surviving only if its instruction accepts that character, and
the jumps and splits are followed between characters to expand the
set, so at every moment the set holds exactly the positions the
pattern could be in having read the text so far. A pattern matches
when, after the last character, some live position sits on the
succeed instruction. I had guessed that stars and alternation
needed backtracking, trying one branch and rewinding to try
another when it failed, which is what it does needs and is also
what makes many regex engines blow up exponentially on a pattern
like a-star repeated against a long run of the letter a, where the
branches to try multiply; Thompson's engine does not rewind, it
carries all the branches forward together as the set of live
positions, so a branch that would fail simply drops out of the set
instead of costing a rewind. That makes the running time the size
of the pattern times the length of the text, flat, with the
catastrophic case that fells backtracking engines simply unable to
arise, and it is the honest reason to build the matcher this way
rather than the easier recursive one. The engine offers a whole
match, does the pattern describe the entire text, and a search,
does it describe any stretch of it, the search being the whole
match tried from each starting position, and it rejects a
malformed pattern, an unmatched parenthesis or a dangling escape,
rather than matching something unintended.
"""

from __future__ import annotations

from loom.errors import Invalid


class _Parser:
    def __init__(self, pattern: str) -> None:
        self._text = pattern
        self._pos = 0

    def _peek(self) -> str | None:
        return self._text[self._pos] if self._pos < len(self._text) else None

    def _advance(self) -> str:
        char = self._text[self._pos]
        self._pos += 1
        return char

    def parse(self) -> tuple:
        node = self._alternation()
        if self._pos != len(self._text):
            raise Invalid(f"unexpected {self._peek()!r} at position {self._pos}")
        return node

    def _alternation(self) -> tuple:
        node = self._concatenation()
        while self._peek() == "|":
            self._advance()
            node = ("alt", node, self._concatenation())
        return node

    def _concatenation(self) -> tuple:
        parts = []
        while self._peek() is not None and self._peek() not in "|)":
            parts.append(self._repetition())
        if not parts:
            return ("empty",)
        node = parts[0]
        for part in parts[1:]:
            node = ("concat", node, part)
        return node

    def _repetition(self) -> tuple:
        node = self._atom()
        while self._peek() in ("*", "+", "?"):
            operator = self._advance()
            node = {"*": "star", "+": "plus", "?": "opt"}[operator], node
        return node

    def _atom(self) -> tuple:
        char = self._peek()
        if char == "(":
            self._advance()
            node = self._alternation()
            if self._peek() != ")":
                raise Invalid("unmatched (")
            self._advance()
            return node
        if char == ".":
            self._advance()
            return ("any",)
        if char == "\\":
            self._advance()
            escaped = self._peek()
            if escaped is None:
                raise Invalid("dangling escape at end of pattern")
            self._advance()
            return ("char", escaped)
        if char in ("*", "+", "?", "|", ")"):
            raise Invalid(f"unexpected {char!r}")
        return ("char", self._advance())


def _emit(node: tuple, program: list) -> None:
    kind = node[0]
    if kind == "empty":
        return
    if kind == "char":
        program.append(["char", node[1]])
    elif kind == "any":
        program.append(["any"])
    elif kind == "concat":
        _emit(node[1], program)
        _emit(node[2], program)
    elif kind == "alt":
        split = ["split", None, None]
        program.append(split)
        split[1] = len(program)
        _emit(node[1], program)
        jump = ["jmp", None]
        program.append(jump)
        split[2] = len(program)
        _emit(node[2], program)
        jump[1] = len(program)
    elif kind == "star":
        anchor = len(program)
        split = ["split", None, None]
        program.append(split)
        split[1] = len(program)
        _emit(node[1], program)
        program.append(["jmp", anchor])
        split[2] = len(program)
    elif kind == "plus":
        anchor = len(program)
        _emit(node[1], program)
        split = ["split", anchor, None]
        program.append(split)
        split[2] = len(program)
    elif kind == "opt":
        split = ["split", None, None]
        program.append(split)
        split[1] = len(program)
        _emit(node[1], program)
        split[2] = len(program)


def _compile(pattern: str) -> list:
    program: list = []
    _emit(_Parser(pattern).parse(), program)
    program.append(["match"])
    return program


def _add_thread(program: list, threads: list, seen: set, counter: int) -> None:
    if counter in seen:
        return
    seen.add(counter)
    operator = program[counter][0]
    if operator == "jmp":
        _add_thread(program, threads, seen, program[counter][1])
    elif operator == "split":
        _add_thread(program, threads, seen, program[counter][1])
        _add_thread(program, threads, seen, program[counter][2])
    else:
        threads.append(counter)


class Regex:
    __slots__ = ("_program", "pattern")

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        self._program = _compile(pattern)

    def fullmatch(self, text: str) -> bool:
        program = self._program
        seen: set = set()
        current: list = []
        _add_thread(program, current, seen, 0)
        for char in text:
            following: list = []
            following_seen: set = set()
            for counter in current:
                operator = program[counter][0]
                if (operator == "char" and program[counter][1] == char) or operator == "any":
                    _add_thread(program, following, following_seen, counter + 1)
            current = following
            if not current:
                break
        return any(program[pc][0] == "match" for pc in current)

    def search(self, text: str) -> bool:
        return any(self._run_from(text, start) for start in range(len(text) + 1))

    def _run_from(self, text: str, start: int) -> bool:
        program = self._program
        seen: set = set()
        current: list = []
        _add_thread(program, current, seen, 0)
        if any(program[pc][0] == "match" for pc in current):
            return True
        for char in text[start:]:
            following: list = []
            following_seen: set = set()
            for counter in current:
                operator = program[counter][0]
                if (operator == "char" and program[counter][1] == char) or operator == "any":
                    _add_thread(program, following, following_seen, counter + 1)
            current = following
            if any(program[pc][0] == "match" for pc in current):
                return True
            if not current:
                break
        return False
