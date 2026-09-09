"""Combinatorics: factorials, permutations, combinations, and Catalan numbers, exactly.

Counting arrangements and selections is combinatorics, and this
computes the standard quantities with exact integer arithmetic,
which matters because these grow enormous fast and a floating
approximation would lose the exact count the moment it mattered.
The factorial is the product of the integers up to n, the number
of ways to arrange n things. Permutations count ordered
selections of k from n, the falling product from n down k terms,
and combinations count unordered ones, the permutations divided
by the k-factorial orderings that are the same selection
unordered. The combination is computed to stay small along the
way, using the symmetry that choosing k from n equals choosing
n minus k so it always works with the smaller, and multiplying
and dividing in step so the intermediate values never exceed the
answer, which keeps even a large binomial exact and cheap rather
than building two vast factorials only to divide most of them
away. The Catalan number, the count of many recursively
structured things from balanced parentheses to binary trees,
falls out of the central binomial. The domain rules are enforced:
a negative argument, or choosing more than there are, is refused
rather than returning a zero or a garbage value that a caller
might use as a real count. Everything returns a Python integer,
which grows without bound, so the results are exact at any size,
the whole reason to compute them here rather than with the
floating factorials a math library's gamma function would give,
which are fast and approximate where these are exact.
"""

from __future__ import annotations

from loom.errors import Invalid


def factorial(n: int) -> int:
    if n < 0:
        raise Invalid("factorial is undefined for negatives")
    result = 1
    for value in range(2, n + 1):
        result *= value
    return result


def permutations(n: int, k: int) -> int:
    if n < 0 or k < 0 or k > n:
        raise Invalid(f"cannot arrange {k} of {n}")
    result = 1
    for value in range(n, n - k, -1):
        result *= value
    return result


def combinations(n: int, k: int) -> int:
    if n < 0 or k < 0 or k > n:
        raise Invalid(f"cannot choose {k} of {n}")
    k = min(k, n - k)
    numerator = 1
    denominator = 1
    for index in range(k):
        numerator *= n - index
        denominator *= index + 1
    return numerator // denominator


def catalan(n: int) -> int:
    if n < 0:
        raise Invalid("Catalan numbers are defined for non-negatives")
    return combinations(2 * n, n) // (n + 1)
