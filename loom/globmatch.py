"""Glob match: match a string against a shell-style glob pattern.

Glob patterns are the wildcards a shell uses to pick names, a
star for any run of characters, a question mark for exactly
one, and a bracket class for one character from a set or a
range, and this matches a string against one. It compiles the
pattern once into tokens, a literal, an any, a star, or a
character class with its set and whether it is negated, so the
matcher works on a clean token list rather than re-parsing the
pattern's brackets and ranges on every step. The match itself
is the standard wildcard recursion made total by memoizing on
the pair of positions, which is what keeps a pattern of many
stars against a long string from blowing up into exponential
backtracking, the classic glob performance trap; every position
pair is decided once. A star matches the empty run or one more
character and recurses, a class matches a character in its set
unless negated, and a literal or any matches one character, and
the pattern matches when both the pattern and the string are
used up together, so a pattern shorter than the string fails
rather than matching a prefix. The negation marker inside a
class is either the exclamation the shell uses or the caret the
regex tradition uses, both accepted since a caller reaches for
whichever they know. It matches a whole string, not a search
within one, because a glob names a thing entire, and a caller
wanting a substring match brackets it with stars themselves,
which is explicit rather than a surprising default.
"""

from __future__ import annotations


def _compile(pattern: str) -> list[tuple]:
    tokens: list[tuple] = []
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "*":
            tokens.append(("star",))
            index += 1
        elif char == "?":
            tokens.append(("any",))
            index += 1
        elif char == "[":
            index += 1
            negate = False
            if index < len(pattern) and pattern[index] in "!^":
                negate = True
                index += 1
            members: set[str] = set()
            while index < len(pattern) and pattern[index] != "]":
                if (
                    index + 2 < len(pattern)
                    and pattern[index + 1] == "-"
                    and pattern[index + 2] != "]"
                ):
                    for code in range(
                        ord(pattern[index]), ord(pattern[index + 2]) + 1
                    ):
                        members.add(chr(code))
                    index += 3
                else:
                    members.add(pattern[index])
                    index += 1
            tokens.append(("class", members, negate))
            index += 1
        else:
            tokens.append(("lit", char))
            index += 1
    return tokens


def _one(token: tuple, char: str) -> bool:
    kind = token[0]
    if kind == "any":
        return True
    if kind == "lit":
        return char == token[1]
    return (char in token[1]) != token[2]


def matches(pattern: str, text: str) -> bool:
    tokens = _compile(pattern)
    memo: dict[tuple[int, int], bool] = {}

    def go(token_index: int, text_index: int) -> bool:
        key = (token_index, text_index)
        if key in memo:
            return memo[key]
        if token_index == len(tokens):
            result = text_index == len(text)
        elif tokens[token_index][0] == "star":
            result = go(token_index + 1, text_index) or (
                text_index < len(text) and go(token_index, text_index + 1)
            )
        else:
            result = text_index < len(text) and _one(
                tokens[token_index], text[text_index]
            ) and go(token_index + 1, text_index + 1)
        memo[key] = result
        return result

    return go(0, 0)
