"""Fit Bradley-Terry team strengths so the exact bracket reach-probabilities
match the (vig-free) betting-market markers.

We have three market markers per team -- win / reach_final / reach_semi -- plus
(optionally) the current round's match odds. We choose one strength theta per
team so the bracket's exact reach-probs line up with them.

Method (v1): heuristic multiplicative updates. For each team we nudge theta up
when the model under-rates how far it goes and down when it over-rates, blending
the three markers. It's monotone and converges fine for this problem; it can be
swapped for a proper optimiser later without touching callers.
"""
from .bracket import reach_markers

# how strongly each marker pulls the fit; the outright-win market is sharpest.
MARKER_WEIGHTS = {"win": 1.0, "reach_final": 0.7, "reach_semi": 0.5}


def calibrate(teams, market, iters=600, lr=0.35, first_round_p=None):
    """`market` = {"win": {team: prob}, "reach_final": {...}, "reach_semi": {...}}
    with each marker already normalised to its known total (1, 2, 4).
    `first_round_p` (optional) fixes the current round to market prices during the
    fit (so already-decided / market-priced first-round ties aren't re-modelled).
    Returns {team: theta}.
    """
    # only fit markers the bracket actually produces at this size (e.g. a 4-team
    # bracket has no "reach_semi" -- everyone is already in the semi-finals)
    probe = reach_markers(teams, {t: 1.0 for t in teams}, first_round_p)
    active = [m for m in MARKER_WEIGHTS if m in market and m in probe]
    theta = {t: 1.0 for t in teams}
    for _ in range(iters):
        model = reach_markers(teams, theta, first_round_p)
        for t in teams:
            log_adj = 0.0
            wsum = 0.0
            for marker in active:
                w = MARKER_WEIGHTS[marker]
                target = market[marker].get(t, 0.0)
                got = model[marker].get(t, 0.0)
                # work in log space; clamp to avoid blow-ups on tiny probs
                tgt = max(target, 1e-6)
                cur = max(got, 1e-6)
                log_adj += w * (_log(tgt) - _log(cur))
                wsum += w
            theta[t] *= _exp(lr * log_adj / wsum)
        _renormalise(theta)
    return theta


def fit_report(teams, theta, market, first_round_p=None):
    """Mean absolute error between fitted reach-probs and market, per marker."""
    model = reach_markers(teams, theta, first_round_p)
    out = {}
    for marker in MARKER_WEIGHTS:
        if marker not in market or marker not in model:
            continue
        errs = [abs(model[marker].get(t, 0.0) - market[marker].get(t, 0.0)) for t in teams]
        out[marker] = sum(errs) / len(errs)
    return out, model


def _renormalise(theta):
    # fix the overall scale (Bradley-Terry is invariant to it) via geometric mean
    n = len(theta)
    g = _exp(sum(_log(v) for v in theta.values()) / n)
    for t in theta:
        theta[t] /= g


# tiny math shims to keep imports obvious
def _log(x):
    import math
    return math.log(x)


def _exp(x):
    import math
    return math.exp(x)
