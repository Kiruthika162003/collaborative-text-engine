"""Calc: evaluate an arithmetic expression, with precedence and parentheses.

This reads a string like one and two times three and computes
it, a small recursive-descent evaluator over the four
operators, parentheses, and unary minus, with the precedence
everyone expects, multiplication and division binding tighter
than addition and subtraction, and parentheses overriding both.
It works in the textbook two steps, a tokenizer that turns the
string into numbers and operator symbols and a parser whose
grammar encodes the precedence directly: an expression is terms
joined by plus and minus, a term is factors joined by times and
divide, and a factor is a number, a parenthesized expression,
or a negated factor, which is exactly the layering that makes
times bind before plus without any precedence table. Division
by zero is refused rather than allowed to raise a bare
arithmetic error, so a caller gets a message in the same
vocabulary as the rest of the failures, and a malformed
expression, a missing parenthesis or a stray symbol or numbers
run together, is refused with what was expected rather than
half-evaluated, because a calculator that guessed past a syntax
error would return a confident wrong number. It evaluates
literal arithmetic only, no variables and no functions and no
exponent, because those are a bigger language and this is the
small one a caller reaches for to turn a typed sum into a
value; a caller who needs the bigger one wants a real
expression language, not this pretending to be it.
"""

from __future__ import annotations

from loom.errors import Invalid

OPERATORS = frozenset("+-*/()")


def _tokenize(expression: str) -> list[tuple]:
    tokens: list[tuple] = []
    index = 0
    while index < len(expression):
        char = expression[index]
        if char.isspace():
            index += 1
        elif char in OPERATORS:
            tokens.append((char, char))
            index += 1
        elif char.isdigit() or char == ".":
            start = index
            while index < len(expression) and (
                expression[index].isdigit() or expression[index] == "."
            ):
                index += 1
            chunk = expression[start:index]
            tokens.append(
                ("num", float(chunk) if "." in chunk else int(chunk))
            )
        else:
            raise Invalid(f"unexpected character {char!r}")
    return tokens


class _Parser:
    def __init__(self, tokens: list[tuple]) -> None:
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> str | None:
        return self.tokens[self.pos][0] if self.pos < len(self.tokens) else None

    def _next(self) -> tuple:
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def expression(self) -> float:
        value = self.term()
        while self._peek() in ("+", "-"):
            operator = self._next()[0]
            right = self.term()
            value = value + right if operator == "+" else value - right
        return value

    def term(self) -> float:
        value = self.factor()
        while self._peek() in ("*", "/"):
            operator = self._next()[0]
            right = self.factor()
            if operator == "*":
                value *= right
            else:
                if right == 0:
                    raise Invalid("division by zero")
                value /= right
        return value

    def factor(self) -> float:
        head = self._peek()
        if head == "-":
            self._next()
            return -self.factor()
        if head == "(":
            self._next()
            value = self.expression()
            if self._peek() != ")":
                raise Invalid("expected a closing parenthesis")
            self._next()
            return value
        if head == "num":
            return self._next()[1]
        raise Invalid("expected a number or a parenthesis")


def evaluate(expression: str) -> float:
    parser = _Parser(_tokenize(expression))
    value = parser.expression()
    if parser.pos != len(parser.tokens):
        raise Invalid("unexpected trailing tokens")
    return value
