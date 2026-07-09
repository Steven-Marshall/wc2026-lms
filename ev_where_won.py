"""Where does the pot get WON — in the semis or at the final? Prices the four
archetypal plays for one player (Huw, who can legally run all four) against a
realistic field: the other five run the save-aware policy with a soft
anti-Argentina reluctance (nobody wants to ride Argentina). Splits each play's
EV into 'won by end of SF' (sole survivor into the final -> final is a formality)
vs 'won at the Final' (a contested final decided it).
    python ev_where_won.py
"""
import os
import random

from lms import data_io
from lms.calibrate import calibrate, fit_report
from lms.ev import round_values, assignment_pick
from lms.simulate import simulate_many, participants, winner_of_match_containing
from lms.strategy import Context

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
N_SIMS = 30000
SEED = 909
TEMP = 0.12
ARG_PENALTY = 2.5          # log-units knocked off Argentina in the rival model
ROUNDS = ["QF", "SF", "Final"]

USED = {
    "Matty":  ["Argentina", "Morocco"],
    "Huw":    ["USA", "Morocco"],
    "Conrad": ["England", "Morocco"],
    "Andrea": ["England", "Morocco"],
    "Malley": ["Belgium", "Morocco"],
    "Hasan":  ["USA", "Argentina"],
}

PLAYS = [
    ("1 safe       Spain/England/France", ["Spain", "England", "France"]),
    ("2 patriot    Spain/France/England", ["Spain", "France", "England"]),
    ("3 burnt-Eng  Spain/Argentina/France", ["Spain", "Argentina", "France"]),
    ("4 keepSpain  France/England/Spain", ["France", "England", "Spain"]),
    ("4b keepSpain France/Argentina/Spain", ["France", "Argentina", "Spain"]),
]


def penalized(values):
    """Copy round_values, knocking Argentina down so rivals shun it."""
    if "Argentina" not in values:
        return values
    v = {t: row[:] for t, row in values.items()}
    v["Argentina"] = [x - ARG_PENALTY for x in v["Argentina"]]
    return v


def rivals_survival(ctx, sim, rivals, rng):
    state = {nm: {"used": set(USED[nm]), "alive": True, "n": 0} for nm in rivals}
    for rnd in ROUNDS:
        parts = participants(sim, rnd)
        vals, kk = round_values(ctx, parts)
        vals = penalized(vals)
        for nm in rivals:
            st = state[nm]
            if not st["alive"]:
                continue
            legal = [t for t in parts if t not in st["used"]]
            if not legal:
                st["alive"] = False
                continue
            pick = assignment_pick(vals, kk, legal, rng, TEMP)
            st["used"].add(pick)
            if winner_of_match_containing(sim, rnd, pick) == pick:
                st["n"] += 1
            else:
                st["alive"] = False
    return {nm: st["n"] for nm, st in state.items()}


def focal_survival(ctx, sim, used0, plan):
    used = set(used0)
    n = 0
    for i, rnd in enumerate(ROUNDS):
        parts = participants(sim, rnd)
        legal = [t for t in parts if t not in used]
        if not legal:
            break
        want = plan[i]
        pick = want if want in legal else max(legal, key=lambda t: ctx.p_win_match(sim, rnd, t))
        used.add(pick)
        if winner_of_match_containing(sim, rnd, pick) == pick:
            n += 1
        else:
            break
    return n


def price(ctx, sims, focal, plan):
    rng = random.Random(SEED)
    rivals = [nm for nm in USED if nm != focal]
    ev = by_sf = at_final = solo = 0.0
    for sim in sims:
        res = rivals_survival(ctx, sim, rivals, rng)
        nf = focal_survival(ctx, sim, USED[focal], plan)
        res["_focal"] = nf
        best = max(res.values())
        if nf == best:
            winners = [k for k, v in res.items() if v == best]
            share = 1.0 / len(winners)
            ev += share
            if len(winners) == 1:
                solo += 1
            reached_final = sum(1 for v in res.values() if v >= 2)
            if reached_final <= 1:      # focal alone into the final (or pot settled earlier)
                by_sf += share
            else:
                at_final += share
    n = len(sims)
    return {"ev": ev / n, "by_sf": by_sf / n, "at_final": at_final / n, "solo": solo / n}


def main():
    d = data_io.load(DATA_DIR)
    teams, market, frp = d["teams"], d["market"], d["match"]
    theta = calibrate(teams, market, first_round_p=frp)
    _, model = fit_report(teams, theta, market, first_round_p=frp)
    ctx = Context(teams, theta, market, model)
    sims = simulate_many(teams, theta, N_SIMS, seed=SEED, first_round_p=frp)
    print(f"Where the pot is won — Huw runs each play vs realistic anti-Arg field")
    print(f"({N_SIMS} sims, temp={TEMP}, Argentina penalty={ARG_PENALTY}). Fair share 16.7%.\n")
    print(f"{'play':40} {'EV':>6} {'wonBySF':>8} {'wonAtFinal':>11} {'solo':>6}")
    print("-" * 76)
    for label, plan in PLAYS:
        r = price(ctx, sims, "Huw", plan)
        print(f"{label:40} {r['ev']*100:5.1f}% {r['by_sf']*100:7.1f}% "
              f"{r['at_final']*100:10.1f}% {r['solo']*100:5.1f}%")


if __name__ == "__main__":
    main()
