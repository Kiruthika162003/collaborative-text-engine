"""Primes: test primality, sieve a range, factorize, and find the next prime.

The prime utilities a caller reaches for, done by the direct
methods that are correct and clear. Primality is trial
division: a number is prime when no integer from two up to its
square root divides it, and stopping at the square root is the
one optimization, since a factor above the root pairs with one
below it that would already have been found. The sieve of
Eratosthenes finds every prime up to a bound by crossing out
each prime's multiples, which is far faster than testing each
number when a caller wants the whole range rather than one
number. Factorization pulls out each prime factor with its
multiplicity by dividing it out repeatedly, so twelve
factorizes to two, two, three and the product of the result is
the input, the property that makes a factorization checkable.
The next prime is the first prime above a number, found by
stepping up and testing. The honest bound is that trial
division and this factorization are fine for the moderate
numbers a caller usually has and slow for the very large ones
cryptography works with, where a probabilistic test and a
sub-exponential factorization are the right tools; this is the
clear implementation for ordinary sizes, named as such rather
than pretending to the scale those methods reach. One and
below are not prime by definition, and a caller factorizing a
number below two is refused, because factorization into primes
is defined for integers greater than one and a zero or a one
has no such factorization to return.
"""

from __future__ import annotations

from loom.errors import Invalid


def is_prime(number: int) -> bool:
    if number < 2:
        return False
    if number < 4:
        return True
    if number % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2
    return True


def sieve(limit: int) -> list[int]:
    if limit < 2:
        return []
    flags = [True] * (limit + 1)
    flags[0] = flags[1] = False
    for candidate in range(2, int(limit**0.5) + 1):
        if flags[candidate]:
            for multiple in range(candidate * candidate, limit + 1, candidate):
                flags[multiple] = False
    return [number for number in range(2, limit + 1) if flags[number]]


def prime_factors(number: int) -> list[int]:
    if number < 2:
        raise Invalid("prime factorization is defined for integers above one")
    factors = []
    divisor = 2
    remaining = number
    while divisor * divisor <= remaining:
        while remaining % divisor == 0:
            factors.append(divisor)
            remaining //= divisor
        divisor += 1
    if remaining > 1:
        factors.append(remaining)
    return factors


def next_prime(number: int) -> int:
    candidate = number + 1
    while not is_prime(candidate):
        candidate += 1
    return candidate
