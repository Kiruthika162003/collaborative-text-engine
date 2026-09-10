"""Roots: find where a function crosses zero, by bracketing safely or by iterating fast.

Finding a root of a function, a value where it equals zero, has two
classic methods here with opposite temperaments. Bisection needs a
bracket, two points where the function has opposite signs, so that a
continuous function must cross zero somewhere between them; it then
repeatedly halves the bracket, keeping whichever half still shows
the sign change, and the root is trapped in an interval that shrinks
by half each step until it is as narrow as asked. Newton's method
needs no bracket, only a starting guess and the function's
derivative; it follows the tangent line at the guess down to where
that line hits zero and takes that as the next guess, which when it
works doubles the number of correct digits each step, converging
far faster than bisection's steady halving. I had assumed Newton was
simply the better method, that quadratic convergence made bisection
obsolete; it is not, and the two fail and succeed in opposite
conditions. Newton can shoot off to nowhere from a bad start, oscillate
without settling, or divide by a zero slope where the tangent is
flat, none of which it detects as it happens, while bisection,
given a valid bracket, cannot fail to converge, guaranteed by the
sign change alone, though it never converges quickly. So the honest
pairing is not one replacing the other but each for what it is good
at: bisection to get safely near a root from a bracket, Newton to
polish it to full precision once close, and the secant method as a
middle option that gets Newton-like speed without needing the
derivative by approximating the slope from the last two points, at
the cost of Newton's guarantee-free failures plus its own flat-line
case. This reports failure, a bracket that does not change sign, a
zero slope, a run that does not settle in the allowed steps, rather
than returning a number that is not actually a root.
"""

from __future__ import annotations

from collections.abc import Callable

from loom.errors import Invalid


def bisection(
    function: Callable[[float], float],
    low: float,
    high: float,
    tolerance: float = 1e-12,
    max_iterations: int = 200,
) -> float:
    f_low = function(low)
    f_high = function(high)
    if f_low == 0:
        return low
    if f_high == 0:
        return high
    if (f_low > 0) == (f_high > 0):
        raise Invalid("the function must change sign across the bracket")
    for _ in range(max_iterations):
        middle = (low + high) / 2
        f_middle = function(middle)
        if f_middle == 0 or (high - low) / 2 < tolerance:
            return middle
        if (f_low > 0) != (f_middle > 0):
            high = middle
        else:
            low = middle
            f_low = f_middle
    return (low + high) / 2


def newton(
    function: Callable[[float], float],
    derivative: Callable[[float], float],
    guess: float,
    tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> float:
    current = guess
    for _ in range(max_iterations):
        value = function(current)
        if abs(value) < tolerance:
            return current
        slope = derivative(current)
        if slope == 0:
            raise Invalid("the derivative is zero; Newton cannot step")
        current = current - value / slope
    raise Invalid("Newton did not converge within the allowed steps")


def secant(
    function: Callable[[float], float],
    first: float,
    second: float,
    tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> float:
    f_first = function(first)
    f_second = function(second)
    for _ in range(max_iterations):
        if abs(f_second) < tolerance:
            return second
        spread = f_second - f_first
        if spread == 0:
            raise Invalid("the secant is flat; cannot step")
        nxt = second - f_second * (second - first) / spread
        first, f_first = second, f_second
        second, f_second = nxt, function(nxt)
    raise Invalid("the secant method did not converge within the allowed steps")
