"""Monte-Carlo: sample whole tournaments from the fitted strengths.

Each simulated tournament records, for every round, the matchups and who won.
That's everything a pick-policy needs: who is alive entering a round, who they
play, and whether a chosen team survives.
"""
import random

from .bracket import make_p, round_names_for, round_pairs


def simulate_one(teams, theta, rng, first_round_p=None):
    """Return {round_name: [(team_a, team_b, winner), ...]} for one tournament.
    Works for any power-of-two field (32-team R32 start or 16-team R16 start).

    `first_round_p` (optional): {team: P(advance)} from the real market match odds
    for the *current* round. When given, the first round is resolved from those
    (accurate) prices instead of the fitted strengths — which the calibration
    under-rates for strong teams stuck in a hard draw. Later rounds use theta."""
    p = make_p(theta)
    survivors = list(teams)
    out = {}
    for ri, rnd in enumerate(round_names_for(len(teams))):
        matches = []
        winners = []
        for a, b in round_pairs(survivors):
            if ri == 0 and first_round_p is not None:
                pa = first_round_p[a] / (first_round_p[a] + first_round_p[b])
            else:
                pa = p(a, b)
            winner = a if rng.random() < pa else b
            matches.append((a, b, winner))
            winners.append(winner)
        out[rnd] = matches
        survivors = winners
    return out


def simulate_many(teams, theta, n_sims, seed=0, first_round_p=None):
    rng = random.Random(seed)
    return [simulate_one(teams, theta, rng, first_round_p) for _ in range(n_sims)]


def participants(sim, rnd):
    """Teams playing in `rnd` of a given sim, in bracket order."""
    teams = []
    for a, b, _ in sim[rnd]:
        teams.append(a)
        teams.append(b)
    return teams


def winner_of_match_containing(sim, rnd, team):
    """Who won the match in `rnd` that `team` played in (None if not playing)."""
    for a, b, w in sim[rnd]:
        if team in (a, b):
            return w
    return None
