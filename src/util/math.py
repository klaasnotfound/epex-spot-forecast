from typing import TypeVar

T = TypeVar("T", int, float)


def normalize(vals: list[T]) -> list[float]:
    s = sum(vals)
    return [(e / s) for e in vals]
