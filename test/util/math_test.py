from src.util.math import normalize


def test_normalize():
    assert [round(v, 1) for v in normalize([1, 2, 3, 4])] == [0.1, 0.2, 0.3, 0.4]
    assert [round(v, 2) for v in normalize([4.0, 2.3, 3.5, 0.2])] == [
        0.4,
        0.23,
        0.35,
        0.02,
    ]
