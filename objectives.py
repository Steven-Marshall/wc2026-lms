"""Two different objectives, two different games.

  EV        = expected share of the pot          (what the model has optimised)
  IN-MONEY  = P(I am among the winners at all)   (what the players seem to optimise
                                                  -- "I just want to win it, even if
                                                  it's a big split")
  SOLO      = P(I take the whole pot alone)

Locks in the reported semi picks and Malley's stated plan (Argentina then France),
best-responds Huw, and reports all three metrics so we can see where the objectives
pull apart.
    python objectives.py
"""
import itertools
import os
from collections import defaultdict

from lms import data_io
from lms.bracket import make_p
from lms.calibrate import calibrate
from endgame_solve import build_worlds, PLAYERS, AVAIL, OUTCOMES

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def strat(semi, team):
    """Fixed plan: this semi pick, and always this team in the final round."""
    return (semi, {o: team for o in OUTCOMES if semi in o})


# Reported / stated plans. Huw is left to best-respond.
FIELD = {
    "Conrad": strat("Argentina", "France"),   # reported
    "Matty":  strat("England", "France"),     # reported (France is his only option)
    "Malley": strat("Argentina", "France"),   # stated: "Arg then France"
    "Andrea": strat("Argentina", "France"),   # assumed (mirrors Conrad)
    "Hasan":  strat("England", "France"),     # assumed (France is his only option)
}


def all_strats(nm):
    out = []
    for semi in AVAIL[nm]:
        rest = [t for t in AVAIL[nm] if t != semi]
        live = [o for o in OUTCOMES if semi in o]
        for c in itertools.product(rest, repeat=len(live)):
            out.append((semi, dict(zip(live, c))))
    return out


def metrics(worlds, profile):
    ev, solo, money = defaultdict(float), defaultdict(float), defaultdict(float)
    for w1, w2, l1, l2, fw, pw, prob in worlds:
        won = {w1, w2}
        alive = [nm for nm in PLAYERS if profile[nm][0] in won] or list(PLAYERS)
        if len(alive) == 1:
            ev[alive[0]] += prob
            solo[alive[0]] += prob
            money[alive[0]] += prob
            continue
        rw = {fw, pw}
        surv = [nm for nm in alive if profile[nm][1].get((w1, w2)) in rw] or alive
        for nm in surv:
            ev[nm] += prob / len(surv)
            money[nm] += prob
        if len(surv) == 1:
            solo[surv[0]] += prob
    return ev, solo, money


def main():
    d = data_io.load(DATA_DIR)
    theta = calibrate(d["teams"], d["market"], first_round_p=d["match"])
    p = make_p(theta)
    worlds = list(build_worlds(p, d["match"]))

    # --- What does Huw do, under each objective? ---
    print("HUW's best response, depending on WHAT HE IS MAXIMISING:\n")
    best = {}
    for key, idx in (("EV", 0), ("SOLO (win outright)", 1), ("IN-MONEY (any win)", 2)):
        bs, bv = None, -1
        for st in all_strats("Huw"):
            prof = dict(FIELD)
            prof["Huw"] = st
            v = metrics(worlds, prof)[idx]["Huw"]
            if v > bv + 1e-12:
                bs, bv = st, v
        picks = "/".join(sorted(set(bs[1].values())))
        print(f"  maximise {key:20} -> semi {bs[0]:10} final {picks:18} = {bv*100:.1f}%")
        best[key] = bs

    # --- Full board with Huw playing the EV-optimal line ---
    prof = dict(FIELD)
    prof["Huw"] = best["EV"]
    ev, solo, money = metrics(worlds, prof)
    print("\n\nTHE BOARD (Huw plays his EV-optimal line)\n")
    print(f"  {'player':8} {'semi':10} {'final':10} {'EV':>6} {'IN-MONEY':>9} {'SOLO':>7}")
    print("  " + "-" * 56)
    for nm in sorted(PLAYERS, key=lambda x: -ev[x]):
        picks = "/".join(sorted(set(prof[nm][1].values())))
        print(f"  {nm:8} {prof[nm][0]:10} {picks:10} {ev[nm]*100:5.1f}% "
              f"{money[nm]*100:8.1f}% {solo[nm]*100:6.1f}%")
    print(f"\n  P(a solo winner at all) = {sum(solo.values())*100:.1f}%")

    # --- the point: what MALLEY threw away ---
    print("\n\nWHAT MALLEY'S 'ARG then FRANCE' COSTS HIM")
    for label, st in (("Arg semi -> FRANCE final  (his stated plan)",
                       strat("Argentina", "France")),
                      ("Arg semi -> ENGLAND final (keeps the defect card)",
                       strat("Argentina", "England")),
                      ("Eng semi -> ARGENTINA final (the model's line)",
                       strat("England", "Argentina"))):
        prof2 = dict(prof)
        prof2["Malley"] = st
        e, s, m = metrics(worlds, prof2)
        print(f"  {label:48} EV={e['Malley']*100:5.1f}%  "
              f"in-money={m['Malley']*100:5.1f}%  solo={s['Malley']*100:5.1f}%")


if __name__ == "__main__":
    main()
