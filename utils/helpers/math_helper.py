import math
from functools import reduce
from typing import Union

Number = Union[int, float]

def _lcm(a: Number, b: Number) -> float:
    """
    Calculate LCM of two numbers (int or float) as a float.
    """
    # Find how many decimal places to scale
    scale = max(_get_decimal_places(a), _get_decimal_places(b))
    factor = 10 ** scale

    # Convert to integers
    a_int = int(round(a * factor))
    b_int = int(round(b * factor))

    # Compute LCM as integer
    lcm_int = abs(a_int * b_int) // math.gcd(a_int, b_int)

    # Scale back to float
    return lcm_int / factor

def _get_decimal_places(x: Number) -> int:
    """
    Returns number of decimal places in a float.
    """
    if isinstance(x, int):
        return 0
    s = str(x)
    if '.' in s:
        return len(s.split('.')[1])
    return 0

def lcm_of_list(numbers: list[Number]) -> float:
    """
    Calculate LCM of a list of numbers (int or float).
    """
    return reduce(_lcm, numbers)