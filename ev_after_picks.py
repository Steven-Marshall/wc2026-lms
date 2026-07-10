"""EV standings with the ACTUAL QF picks locked in: Huw took England, everyone
else took Spain. QF pick is fixed; SF/Final run the save-aware assignment policy.
The five herd players carry a soft anti-Argentina reluctance. Huw is run both
ways: willing to ride Argentina in the semi, and squeamish about it.
    python ev_after_picks.py
"""
import os
import random

from lms import data_io
from lms.calibrate import calibrate, fit_report
from lms.ev import round_values, assignment_pick
from lms.simulate import simulate_many, participants, winner_of_match_containing
from lms.strategy import Context

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
N_SIMS = 40000
SEED = 909
TEMP = 0.12
ARG_PEN = 2.5
ROUNDS = ["QF", "SF", "Final"]

USED = {
    "Huw":    ["USA", "Morocco"],
    "Matty":  ["Argentina", "Morocco"],
    "Malley": ["Belgium", "Morocco"],
    "Hasan":  ["USA", "Argentina"],
    "Conrad": ["England", "Morocco"],
    "Andrea": ["England", "Morocco"],
}
QF_PICK = {"Huw": "England", "Matty": "Spain", "Malley": "Spain",
           "Hasan": "Spain", "Conrad": "Spain", "Andrea": "Spain"}


def penalize(values, pen):
    if "Argentina" not in values or pen <= 0:
        return values
    v = {t: row[:] for t, row in values.items()}
    v["Argentina"] = [x - pen for x in v["Argentina"]]
    return v


def run_sim(ctx, sim, rng, huw_shuns_arg):
    state = {nm: {"used": set(USED[nm]), "alive": True, "n": 0} for nm in USED}
    for ri, rnd in enumerate(ROUNDS):
        parts = participants(sim, rnd)
        vals, kk = round_values(ctx, parts)
        herd_vals = penalize(vals, ARG_PEN)
        huw_vals = penalize(vals, ARG_PEN if huw_shuns_arg else 0.0)
        for nm, st in state.items():
            if not st["alive"]:
                continue
            legal = [t for t in parts if t not in st["used"]]
            if not legal:
                st["alive"] = False
                continue
            if ri == 0:
                pick = QF_PICK[nm] if QF_PICK[nm] in legal else legal[0]
            else:
                v = huw_vals if nm == "Huw" else herd_vals
                pick = assignment_pick(v, kk, legal, rng, TEMP)
            st["used"].add(pick)
            if winner_of_match_containing(sim, rnd, pick) == pick:
                st["n"] += 1
            else:
                st["alive"] = False
    return {nm: st["n"] for nm, st in state.items()}


def evaluate(ctx, sims, huw_shuns_arg):
    rng = random.Random(SEED)
    agg = {nm: {"ev": 0.0, "solo": 0, "qfwin": 0} for nm in USED}
    for sim in sims:
        res = run_sim(ctx, sim, rng, huw_shuns_arg)
        best = max(res.values())
        winners = [nm for nm, k in res.items() if k == best]
        for nm in USED:
            if res[nm] == best:
                agg[nm]["ev"] += 1.0 / len(winners)
                if len(winners) == 1:
                    agg[nm]["solo"] += 1
        # "won it at the QF": sole player to survive round 0
        survived_qf = [nm for nm in USED if res[nm] >= 1]
        if len(survived_qf) == 1:
            agg[survived_qf[0]]["qfwin"] += 1
    n = len(sims)
    return {nm: {"ev": a["ev"] / n, "solo": a["solo"] / n, "qfwin": a["qfwin"] / n}
            for nm, a in agg.items()}


def show(title, r):
    print(f"\n{title}")
    print(f"  {'player':8} {'QF pick':9} {'EV':>6} {'solo':>7} {'wins@QF':>8}")
    for nm in sorted(USED, key=lambda x: -r[x]["ev"]):
        print(f"  {nm:8} {QF_PICK[nm]:9} {r[nm]['ev']*100:5.1f}% "
              f"{r[nm]['solo']*100:6.1f}% {r[nm]['qfwin']*100:7.1f}%")


def main():
    d = data_io.load(DATA_DIR)
    teams, market, frp = d["teams"], d["market"], d["match"]
    theta = calibrate(teams, market, first_round_p=frp)
    _, model = fit_report(teams, theta, market, first_round_p=frp)
    ctx = Context(teams, theta, market, model)
    sims = simulate_many(teams, theta, N_SIMS, seed=SEED, first_round_p=frp)
    print(f"QF picks locked: Huw=England, everyone else=Spain. ({N_SIMS} sims)")
    print("Fair share = 16.7%.  'wins@QF' = sole survivor of the quarter-finals.")
    show("=== Huw willing to ride Argentina in the semi ===",
         evaluate(ctx, sims, huw_shuns_arg=False))
    show("=== Huw squeamish, shuns Argentina too ===",
         evaluate(ctx, sims, huw_shuns_arg=True))


if __name__ == "__main__":
    main()
