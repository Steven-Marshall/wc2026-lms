"""Load the bracket + market data files and turn the raw odds into the
vig-free market markers the calibrator expects.
"""
import os

from . import jsonc, odds
from .bracket import round_pairs


def load(data_dir):
    bracket = jsonc.load(os.path.join(data_dir, "bracket.jsonc"))
    markets = jsonc.load(os.path.join(data_dir, "markets.jsonc"))
    teams = bracket["teams"]
    n = len(teams)
    if n < 2 or (n & (n - 1)) != 0:
        raise ValueError(f"team count must be a power of two (2..32), got {n}")

    # totals are stage-invariant: 1 champion, 2 finalists, 4 semi-finalists
    market = {}
    for marker, total in (("win", 1.0), ("reach_final", 2.0), ("reach_semi", 4.0)):
        if marker in markets:
            market[marker] = odds.market_to_probs(markets[marker], total)
    # current-round match odds -> per-match P(win), using the bracket pairings
    match = None
    if "match" in markets:
        match = odds.match_probs(markets["match"], round_pairs(teams))
    return {"teams": teams, "market": market, "match": match, "current_round":
            markets.get("current_round", "R32")}
