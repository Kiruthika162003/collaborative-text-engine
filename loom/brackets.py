"""Brackets: match the parentheses and braces, and point at the one that has no partner.

Matching brackets is the check an editor runs so a writer
sees the unclosed paren before the compiler does, and it is
a stack: every opener waits on the stack for its own kind of
closer, a closer that finds the right opener on top pops it,
and a closer that finds the wrong kind or an empty stack is
a mismatch with a position worth naming. What survives at
the end of the scan is the openers nobody closed, and the
report points at the first of each kind of trouble, the
first stray closer and the first lonely opener, because a
writer fixing a document wants the earliest error, not a
count. The matcher also answers the other question an editor
asks, where is the partner of the bracket under the caret,
walking forward from an opener or back from a closer through
the nesting to the bracket that pairs with it, and returning
nothing when the brackets are tangled rather than guessing a
partner that is not really one. The simplification is stated
plainly: this reads brackets in the raw text and does not
know that a parenthesis inside a code fence or a quoted
string is not structural, so a document full of code is
better checked with the fences skipped first, and the
matcher says so rather than pretending a smiley's paren is
an unbalanced bracket without comment.
"""

from __future__ import annotations

from dataclasses import dataclass

PAIRS = {"(": ")", "[": "]", "{": "}"}
CLOSERS = {closer: opener for opener, closer in PAIRS.items()}


@dataclass(frozen=True)
class BalanceReport:
    balanced: bool
    unmatched_open: int | None
    unmatched_close: int | None


def balance(text: str) -> BalanceReport:
    stack: list[tuple[str, int]] = []
    unmatched_close: int | None = None
    for index, char in enumerate(text):
        if char in PAIRS:
            stack.append((char, index))
        elif char in CLOSERS:
            if stack and stack[-1][0] == CLOSERS[char]:
                stack.pop()
            elif unmatched_close is None:
                unmatched_close = index
    unmatched_open = stack[0][1] if stack else None
    return BalanceReport(
        balanced=unmatched_open is None and unmatched_close is None,
        unmatched_open=unmatched_open,
        unmatched_close=unmatched_close,
    )


def is_balanced(text: str) -> bool:
    return balance(text).balanced


def match_at(text: str, index: int) -> int | None:
    if not 0 <= index < len(text):
        return None
    char = text[index]
    if char in PAIRS:
        depth = 0
        for cursor in range(index, len(text)):
            here = text[cursor]
            if here in PAIRS:
                depth += 1
            elif here in CLOSERS:
                depth -= 1
                if depth == 0:
                    return cursor if here == PAIRS[char] else None
        return None
    if char in CLOSERS:
        depth = 0
        for cursor in range(index, -1, -1):
            here = text[cursor]
            if here in CLOSERS:
                depth += 1
            elif here in PAIRS:
                depth -= 1
                if depth == 0:
                    return cursor if here == CLOSERS[char] else None
        return None
    return None


def depth_at(text: str, index: int) -> int:
    stack: list[str] = []
    for char in text[:index]:
        if char in PAIRS:
            stack.append(char)
        elif char in CLOSERS and stack and stack[-1] == CLOSERS[char]:
            stack.pop()
    return len(stack)


def report(text: str) -> str:
    found = balance(text)
    if found.balanced:
        return "brackets balanced"
    parts = []
    if found.unmatched_close is not None:
        parts.append(
            f"stray closer at {found.unmatched_close}"
        )
    if found.unmatched_open is not None:
        parts.append(
            f"unclosed opener at {found.unmatched_open}"
        )
    return "; ".join(parts)
