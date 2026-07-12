"""Solve the endgame as a GAME: best-response iteration over full strategies.

A strategy = (semi pick, final-round pick for each semi outcome you survive).
Players see the semi results before making their final-round pick, so the
final-round choice is contingent on the semi outcome.

    python endgame_solve.py
"""
import itertools
import os
from collections import defaultdict

from lms import data_io
from lms.bracket import make_p
from lms.calibrate import calibrate

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SEMI1 = ("France", "Spain")
SEMI2 = ("England", "Argentina")
FOUR = ["France", "Spain", "England", "Argentina"]
OUTCOMES = [(a, b) for a in SEMI1 for b in SEMI2]

BURNED = {
    "Huw":    {"England"},
    "Malley": {"Spain"},
    "Matty":  {"Spain", "Argentina"},
    "Hasan":  {"Spain", "Argentina"},
    "Conrad": {"Spain", "England"},
    "Andrea": {"Spain", "England"},
}
PLAYERS = list(BURNED)
AVAIL = {nm: [t for t in FOUR if t not in BURNED[nm]] for nm in PLAYERS}


def build_worlds(p, frp):
    """Semi results from the real MARKET match prices (frp); the final and the
    3rd/4th playoff from the fitted strengths (no market exists for those yet)."""
    for w1 in SEMI1:
        l1 = SEMI1[0] if w1 == SEMI1[1] else SEMI1[1]
        for w2 in SEMI2:
            l2 = SEMI2[0] if w2 == SEMI2[1] else SEMI2[1]
            base = frp[w1] * frp[w2]
            for fw in (w1, w2):
                fl = w2 if fw == w1 else w1
                for pw in (l1, l2):
                    pl = l2 if pw == l1 else l1
                    yield w1, w2, l1, l2, fw, pw, base * p(fw, fl) * p(pw, pl)


def strategies(nm):
    """All (semi, final_map) strategies. final_map: {(w1,w2): team}."""
    out = []
    for semi in AVAIL[nm]:
        rest = [t for t in AVAIL[nm] if t != semi]
        live = [o for o in OUTCOMES if semi in o]          # outcomes he survives
        for combo in itertools.product(rest, repeat=len(live)):
            fmap = dict(zip(live, combo))
            out.append((semi, fmap))
    return out


def evaluate(worlds, profile):
    ev = defaultdict(float)
    for w1, w2, l1, l2, fw, pw, prob in worlds:
        won = {w1, w2}
        alive = [nm for nm in PLAYERS if profile[nm][0] in won]
        if not alive:
            alive = list(PLAYERS)                            # all-lose -> all continue
        if len(alive) == 1:
            ev[alive[0]] += prob                            # last man standing
            continue
        rw = {fw, pw}
        surv = [nm for nm in alive if profile[nm][1].get((w1, w2)) in rw]
        if not surv:
            surv = alive                                    # all-lose -> joint winners
        s = prob / len(surv)
        for nm in surv:
            ev[nm] += s
    return ev


def best_response(worlds, profile, nm):
    best, bev = None, -1.0
    for st in strategies(nm):
        trial = dict(profile)
        trial[nm] = st
        e = evaluate(worlds, trial)[nm]
        if e > bev + 1e-12:
            best, bev = st, e
    return best, bev


def describe(st):
    semi, fmap = st
    parts = [f"{w1[:3]}/{w2[:3]}->{t}" for (w1, w2), t in sorted(fmap.items())]
    return f"semi={semi:10} final: " + ", ".join(parts)


def main():
    d = data_io.load(DATA_DIR)
    theta = calibrate(d["teams"], d["market"], first_round_p=d["match"])
    p = make_p(theta)
    frp = d["match"]
    worlds = list(build_worlds(p, frp))
    print("Semi (market):  " + "  ".join(f"{t} {frp[t]*100:.1f}%" for t in FOUR))
    print("Final/playoff head-to-heads (fitted):")
    for a in FOUR:
        print("   " + "  ".join(f"{a[:3]}>{b[:3]} {p(a,b)*100:4.1f}%"
                                for b in FOUR if b != a))
    print()

    # start from the naive profile: save France, spend the other, play France
    profile = {}
    for nm in PLAYERS:
        semi = next(t for t in AVAIL[nm] if t != "France")
        live = [o for o in OUTCOMES if semi in o]
        profile[nm] = (semi, {o: "France" for o in live})

    ev = evaluate(worlds, profile)
    print("START (naive: everyone saves France and plays it in the final round)")
    for nm in sorted(PLAYERS, key=lambda x: -ev[x]):
        print(f"  {nm:8} {describe(profile[nm]):58} EV={ev[nm]*100:5.1f}%")

    print("\nBest-response iteration...")
    for it in range(60):
        changed = False
        for nm in PLAYERS:
            cur = evaluate(worlds, profile)[nm]
            st, bev = best_response(worlds, profile, nm)
            if bev > cur + 1e-9 and st != profile[nm]:
                profile[nm] = st
                changed = True
        if not changed:
            print(f"  converged after {it} sweeps -> pure Nash equilibrium")
            break
    else:
        print("  did not converge (cycling) — no pure equilibrium from this start")

    ev = evaluate(worlds, profile)
    print("\nEQUILIBRIUM")
    for nm in sorted(PLAYERS, key=lambda x: -ev[x]):
        print(f"  {nm:8} {describe(profile[nm]):58} EV={ev[nm]*100:5.1f}%")
    print(f"  (total {sum(ev.values())*100:.1f}%)")

    print("\nSemi picks at equilibrium:")
    tally = defaultdict(list)
    for nm in PLAYERS:
        tally[profile[nm][0]].append(nm)
    for t, who in tally.items():
        print(f"  {t:10} {', '.join(who)}")


if __name__ == "__main__":
    main()
