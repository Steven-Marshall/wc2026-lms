"""Convert decimal betting odds into calibrated probabilities.

Odds are entered as the *price* for a $1 stake (decimal/European odds), e.g.
England 7.5 means a winning $1 bet returns $7.50. Implied probability = 1/price.

Two real-world wrinkles, both handled here:

1. Bid/ask (back/lay) spread, e.g. "7.4/7.6". Enter as a two-element list
   [7.4, 7.6]; we take the mid price. A single number is used as-is.

2. Overround (the bookmaker margin) means raw implied probabilities do NOT sum
   to 100%. We never trust the raw numbers as probabilities -- instead we
   normalise each market to its *known* total:
       - match (one winner)      -> 1
       - reach-semi (last 4)     -> 4
       - reach-final (last 2)    -> 2
       - win (champion)          -> 1
   This strips the vig in a principled way and is the input to calibration.
"""


def mid_price(odds):
    """Accept a decimal price (number) or a [bid, ask] pair; return the mid."""
    if isinstance(odds, (list, tuple)):
        if len(odds) != 2:
            raise ValueError(f"bid/ask odds must have 2 elements, got {odds!r}")
        return (float(odds[0]) + float(odds[1])) / 2.0
    return float(odds)


def implied_prob(odds):
    """Raw implied probability from a decimal price (before vig removal)."""
    price = mid_price(odds)
    if price <= 1.0:
        raise ValueError(f"decimal odds must be > 1.0, got {price}")
    return 1.0 / price


def normalize(prob_by_team, target_total):
    """Scale a dict of raw implied probs so they sum to `target_total`."""
    s = sum(prob_by_team.values())
    if s <= 0:
        raise ValueError("probabilities sum to zero; nothing to normalise")
    return {t: p * target_total / s for t, p in prob_by_team.items()}


def market_to_probs(odds_by_team, target_total):
    """Full pipeline: {team: odds} -> vig-free {team: probability}."""
    raw = {t: implied_prob(o) for t, o in odds_by_team.items()}
    return normalize(raw, target_total)


def match_probs(odds_by_team, pairs):
    """Per-match normalisation: each pair's two probs are scaled to sum to 1.

    `pairs` is a list of (team_a, team_b). Returns {team: P(win its match)}.
    """
    out = {}
    for a, b in pairs:
        pa = implied_prob(odds_by_team[a])
        pb = implied_prob(odds_by_team[b])
        tot = pa + pb
        out[a] = pa / tot
        out[b] = pb / tot
    return out
