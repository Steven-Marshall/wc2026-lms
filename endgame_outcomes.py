"""Outcome distribution at the equilibrium: how often is there a SOLO winner,
how often does the pot split, and who can actually win outright?
    python endgame_outcomes.py
"""
import os
from collections import defaultdict

from lms import data_io
from lms.bracket import make_p
from lms.calibrate import calibrate
from endgame_solve import build_worlds, PLAYERS, AVAIL, FOUR

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

EQ = {
    "Huw":    ("France",    {("France", "England"): "Spain",
                             ("France", "Argentina"): "Spain"}),
    "Conrad": ("Argentina", {("France", "Argentina"): "France",
                             ("Spain", "Argentina"): "France"}),
    "Andrea": ("Argentina", {("France", "Argentina"): "France",
                             ("Spain", "Argentina"): "France"}),
    "Malley": ("England",   {("France", "England"): "Argentina",
                             ("Spain", "England"): "Argentina"}),
    "Matty":  ("England",   {("France", "England"): "France",
                             ("Spain", "England"): "France"}),
    "Hasan":  ("England",   {("France", "England"): "France",
                             ("Spain", "England"): "France"}),
}


def main():
    d = data_io.load(DATA_DIR)
    theta = calibrate(d["teams"], d["market"], first_round_p=d["match"])
    p = make_p(theta)
    worlds = list(build_worlds(p, d["match"]))

    solo = defaultdict(float)          # P(this player wins outright, alone)
    split_size = defaultdict(float)    # P(pot splits N ways)
    ev = defaultdict(float)
    p_solo_any = 0.0
    played_france = defaultdict(float)  # P(you play France in the final round)
    france_solo = 0.0

    for w1, w2, l1, l2, fw, pw, prob in worlds:
        won = {w1, w2}
        alive = [nm for nm in PLAYERS if EQ[nm][0] in won]
        if not alive:
            alive = list(PLAYERS)
        if len(alive) == 1:
            solo[alive[0]] += prob
            p_solo_any += prob
            split_size[1] += prob
            ev[alive[0]] += prob
            continue
        rw = {fw, pw}
        picks = {nm: EQ[nm][1][(w1, w2)] for nm in alive}
        for nm, pk in picks.items():
            if pk == "France":
                played_france[nm] += prob
        surv = [nm for nm in alive if picks[nm] in rw]
        if not surv:
            surv = alive                       # all-lose -> joint winners
        split_size[len(surv)] += prob
        if len(surv) == 1:
            solo[surv[0]] += prob
            p_solo_any += prob
            if picks[surv[0]] == "France":
                france_solo += prob
        for nm in surv:
            ev[nm] += prob / len(surv)

    print("OUTCOME DISTRIBUTION AT EQUILIBRIUM\n")
    print(f"  P(a SOLO winner — one man takes the whole pot) = {p_solo_any*100:5.1f}%")
    print(f"  P(the pot is SPLIT)                           = {(1-p_solo_any)*100:5.1f}%\n")
    print("  How many share the pot:")
    for k in sorted(split_size):
        print(f"     {k}-way {'(solo win)' if k == 1 else '        '}  {split_size[k]*100:5.1f}%")

    print("\n  Who can actually win OUTRIGHT?")
    for nm in sorted(PLAYERS, key=lambda x: -solo[x]):
        pct = solo[nm] * 100
        tag = "" if pct > 0.05 else "   <- CANNOT EVER WIN ALONE"
        print(f"     {nm:8} solo={pct:5.1f}%   (EV {ev[nm]*100:4.1f}%){tag}")

    print(f"\n  P(a player who PLAYED FRANCE in the final round wins solo) = "
          f"{france_solo*100:.1f}%")
    print("\n  P(you play France in the final round | you're still alive):")
    for nm in sorted(PLAYERS, key=lambda x: -played_france[x]):
        if played_france[nm] > 0:
            print(f"     {nm:8} {played_france[nm]*100:5.1f}% of all worlds")


if __name__ == "__main__":
    main()
