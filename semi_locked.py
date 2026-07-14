"""Semi picks are coming in. Lock them, then solve the FINAL-ROUND subgame
exactly (best-response iteration on final-round picks, which are made after the
semi results are known but simultaneously with each other).

    python semi_locked.py
"""
import itertools
import os
from collections import defaultdict

from lms import data_io
from lms.bracket import make_p
from lms.calibrate import calibrate
from endgame_solve import build_worlds, PLAYERS, AVAIL, OUTCOMES, FOUR

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---- ACTUAL semi picks as reported -------------------------------------------
# Conrad -> Argentina (equilibrium), Matty -> England (equilibrium),
# Malley  -> Argentina (SWAPPED: model said England then Argentina).
# Huw / Hasan / Andrea not in yet -> assume their equilibrium semi for now.
SEMI_EQ = {"Huw": "France", "Malley": "England", "Matty": "England",
           "Hasan": "England", "Conrad": "Argentina", "Andrea": "Argentina"}
SEMI_ACTUAL = dict(SEMI_EQ)
SEMI_ACTUAL["Malley"] = "Argentina"          # <- the swap


def final_strats(nm, semi):
    rest = [t for t in AVAIL[nm] if t != semi]
    live = [o for o in OUTCOMES if semi in o]
    return [dict(zip(live, c)) for c in itertools.product(rest, repeat=len(live))]


def outcome(worlds, semi, final):
    ev, solo = defaultdict(float), defaultdict(float)
    for w1, w2, l1, l2, fw, pw, prob in worlds:
        won = {w1, w2}
        alive = [nm for nm in PLAYERS if semi[nm] in won] or list(PLAYERS)
        if len(alive) == 1:
            ev[alive[0]] += prob
            solo[alive[0]] += prob
            continue
        rw = {fw, pw}
        surv = [nm for nm in alive if final[nm].get((w1, w2)) in rw] or alive
        for nm in surv:
            ev[nm] += prob / len(surv)
        if len(surv) == 1:
            solo[surv[0]] += prob
    return ev, solo


def solve_final(worlds, semi):
    final = {nm: {o: "France" if "France" in AVAIL[nm] and o[0] != semi[nm] or True
                  else None for o in [x for x in OUTCOMES if semi[nm] in x]}
             for nm in PLAYERS}
    # start everyone on their first legal option
    final = {nm: final_strats(nm, semi[nm])[0] for nm in PLAYERS}
    for _ in range(60):
        changed = False
        for nm in PLAYERS:
            cur = outcome(worlds, semi, final)[0][nm]
            best, bev = final[nm], cur
            for st in final_strats(nm, semi[nm]):
                trial = dict(final)
                trial[nm] = st
                e = outcome(worlds, semi, trial)[0][nm]
                if e > bev + 1e-12:
                    best, bev = st, e
            if best != final[nm]:
                final[nm] = best
                changed = True
        if not changed:
            break
    return final


def report(worlds, semi, label):
    final = solve_final(worlds, semi)
    ev, solo = outcome(worlds, semi, final)
    print(f"\n=== {label} ===")
    camps = defaultdict(list)
    for nm in PLAYERS:
        camps[semi[nm]].append(nm)
    for t, who in camps.items():
        print(f"   semi {t:10}: {', '.join(who)}")
    print(f"\n   {'player':8} {'semi':10} {'final round':28} {'EV':>6} {'solo':>7}")
    for nm in sorted(PLAYERS, key=lambda x: -ev[x]):
        picks = "/".join(sorted(set(final[nm].values())))
        print(f"   {nm:8} {semi[nm]:10} {picks:28} {ev[nm]*100:5.1f}% {solo[nm]*100:6.1f}%")
    tot_solo = sum(solo.values())
    print(f"   P(solo winner) = {tot_solo*100:.1f}%")
    return ev, solo


def main():
    d = data_io.load(DATA_DIR)
    theta = calibrate(d["teams"], d["market"], first_round_p=d["match"])
    p = make_p(theta)
    worlds = list(build_worlds(p, d["match"]))

    ev0, solo0 = report(worlds, SEMI_EQ, "MODEL EQUILIBRIUM (Malley: England semi)")
    ev1, solo1 = report(worlds, SEMI_ACTUAL, "ACTUAL (Malley SWAPS to Argentina semi)")

    print("\n\n   Effect of Malley's swap:")
    print(f"   {'player':8} {'EV before':>10} {'EV after':>9} {'delta':>7}   "
          f"{'solo before':>11} {'solo after':>10}")
    for nm in sorted(PLAYERS, key=lambda x: -(ev1[x] - ev0[x])):
        print(f"   {nm:8} {ev0[nm]*100:9.1f}% {ev1[nm]*100:8.1f}% "
              f"{(ev1[nm]-ev0[nm])*100:+6.1f}   {solo0[nm]*100:10.1f}% "
              f"{solo1[nm]*100:9.1f}%")


if __name__ == "__main__":
    main()
