"""Sanity tests for the odds math. Run: python tests/test_odds.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lms import odds  # noqa: E402


def approx(a, b, tol=1e-9):
    assert abs(a - b) < tol, f"{a} != {b}"


def test_mid_and_implied():
    approx(odds.mid_price([7.4, 7.6]), 7.5)
    approx(odds.mid_price(7.5), 7.5)
    approx(odds.implied_prob(7.5), 1 / 7.5)
    approx(odds.implied_prob([7.4, 7.6]), 1 / 7.5)


def test_normalize_to_known_total():
    # reach-final market must sum to 2 (two finalists), regardless of overround
    raw = {"a": 2.0, "b": 3.0, "c": 4.0, "d": 5.0}  # decimal prices
    probs = odds.market_to_probs(raw, 2.0)
    approx(sum(probs.values()), 2.0)
    # ordering preserved: shortest price -> highest probability
    assert probs["a"] > probs["b"] > probs["c"] > probs["d"]


def test_match_probs_sum_to_one_per_pair():
    raw = {"x": 1.5, "y": 2.5, "p": 4.0, "q": 1.25}
    mp = odds.match_probs(raw, [("x", "y"), ("p", "q")])
    approx(mp["x"] + mp["y"], 1.0)
    approx(mp["p"] + mp["q"], 1.0)
    assert mp["x"] > mp["y"] and mp["q"] > mp["p"]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all odds tests passed")
