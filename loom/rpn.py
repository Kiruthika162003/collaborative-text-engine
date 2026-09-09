"""RPN: evaluate postfix expressions and convert infix to postfix by shunting yard.

Reverse Polish notation writes the operator after its operands,
three four plus rather than three plus four, and it needs no
parentheses because the order of operations is fixed by the
order of the tokens, which is why it evaluates with a simple
stack: push a number, and on an operator pop two numbers, apply
it, and push the result, leaving one value at the end. This
evaluates postfix that way and converts ordinary infix to it by
the shunting-yard algorithm, which reads infix left to right and
moves operators through a holding stack, emitting a held
operator before a new one of equal or higher precedence so the
output honours precedence, and matching parentheses to override
it. Together they are the other approach to the calc module's
recursive descent: same result, a different classic method,
which is worth having explicit because the shunting yard is the
algorithm behind many small expression compilers and seeing it
plainly is instructive in an engine about structure. Tokens are
space-separated, which sidesteps the tokenizing so the algorithm
stands clear, and a caller with a run-together expression
tokenizes first or uses the calc module that does. Division by
zero is refused rather than raising a bare error, a mismatched
parenthesis is caught in the conversion rather than producing
malformed postfix, and a postfix expression that does not reduce
to exactly one value, too few operands for its operators or too
many, is refused as the malformed input it is rather than
returning whichever value happened to be left on the stack.
"""

from __future__ import annotations

from loom.errors import Invalid

PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2}


def eval_postfix(expression: str) -> float:
    stack: list[float] = []
    for token in expression.split():
        if token in PRECEDENCE:
            if len(stack) < 2:
                raise Invalid("too few operands")
            right = stack.pop()
            left = stack.pop()
            if token == "+":
                stack.append(left + right)
            elif token == "-":
                stack.append(left - right)
            elif token == "*":
                stack.append(left * right)
            else:
                if right == 0:
                    raise Invalid("division by zero")
                stack.append(left / right)
        else:
            stack.append(float(token) if "." in token else int(token))
    if len(stack) != 1:
        raise Invalid("the expression does not reduce to one value")
    return stack[0]


def to_postfix(infix: str) -> str:
    output: list[str] = []
    operators: list[str] = []
    for token in infix.split():
        if token in PRECEDENCE:
            while (
                operators
                and operators[-1] != "("
                and PRECEDENCE[operators[-1]] >= PRECEDENCE[token]
            ):
                output.append(operators.pop())
            operators.append(token)
        elif token == "(":
            operators.append(token)
        elif token == ")":
            while operators and operators[-1] != "(":
                output.append(operators.pop())
            if not operators:
                raise Invalid("mismatched closing parenthesis")
            operators.pop()
        else:
            output.append(token)
    while operators:
        if operators[-1] == "(":
            raise Invalid("mismatched opening parenthesis")
        output.append(operators.pop())
    return " ".join(output)


def evaluate(infix: str) -> float:
    return eval_postfix(to_postfix(infix))
