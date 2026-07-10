"""What does adding the 3rd/4th-place playoff ALONGSIDE the final do to the pool?

Under the proposed rule the final round has FOUR teams playing (2 finalists + the
2 beaten semi-finalists). You may pick any of them; you survive the round if your
pick wins ITS match. Rounds-survived is what the pot pays, so winning the
3rd-place playoff scores exactly the same as winning the World Cup.

Compares current rules vs playoff rules on the SAME simulated tournaments.
    python playoff_rules.py
"""
import os
import random

from lms import data_io
from lms.calibrate import calibrate, fit_report
from lms.bracket import make_p
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


def add_playoff(sim, p, rng):
    """Append the 3rd/4th playoff (the two beaten semi-finalists) to the Final round."""
    losers = [(b if w == a else a) for a, b, w in sim["SF"]]
    l1, l2 = losers
    w = l1 if rng.random() < p(l1, l2) else l2
    new = dict(sim)
    new["Final"] = list(sim["Final"]) + [(l1, l2, w)]
    return new


def penalize(values, pen):
    if "Argentina" not in values or pen <= 0:
        return values
    v = {t: row[:] for t, row in values.items()}
    v["Argentina"] = [x - pen for x in v["Argentina"]]
    return v


def run_sim(ctx, sim, rng):
    """Returns (rounds_survived, final_pick, stranded_at_final) per player."""
    state = {nm: {"used": set(USED[nm]), "alive": True, "n": 0,
                  "fp": None, "strand": False} for nm in USED}
    for ri, rnd in enumerate(ROUNDS):
        parts = participants(sim, rnd)
        if rnd != "Final":
            vals, kk = round_values(ctx, parts)
            herd = penalize(vals, ARG_PEN)
        for nm, st in state.items():
            if not st["alive"]:
                continue
            legal = [t for t in parts if t not in st["used"]]
            if not legal:
                st["alive"] = False
                if rnd == "Final":
                    st["strand"] = True
                continue
            if ri == 0:
                pick = QF_PICK[nm] if QF_PICK[nm] in legal else legal[0]
            elif rnd == "Final":
                # last round: no future value -> maximise P(win my own match).
                pick = max(legal, key=lambda t: ctx.p_win_match(sim, rnd, t))
                st["fp"] = pick
            else:
                v = herd if nm != "Huw" else penalize(vals, 0.0)
                pick = assignment_pick(v, kk, legal, rng, TEMP)
            st["used"].add(pick)
            if winner_of_match_containing(sim, rnd, pick) == pick:
                st["n"] += 1
            else:
                st["alive"] = False
    return state


def evaluate(ctx, sims, playoff, p, label):
    rng = random.Random(SEED)
    prng = random.Random(SEED + 1)
    agg = {nm: {"ev": 0.0, "solo": 0, "strand": 0} for nm in USED}
    nwin_tot = 0.0
    split_ge2 = 0
    champ_is_finalist = 0
    winners_via_playoff = 0
    pot_decided = 0
    for sim in sims:
        s = add_playoff(sim, p, prng) if playoff else sim
        finalists = [s["Final"][0][0], s["Final"][0][1]]
        st = run_sim(ctx, s, rng)
        ns = {nm: st[nm]["n"] for nm in USED}
        best = max(ns.values())
        winners = [nm for nm, n in ns.items() if n == best]
        nwin_tot += len(winners)
        if len(winners) >= 2:
            split_ge2 += 1
        for nm in USED:
            if ns[nm] == best:
                agg[nm]["ev"] += 1.0 / len(winners)
                if len(winners) == 1:
                    agg[nm]["solo"] += 1
            if st[nm]["strand"]:
                agg[nm]["strand"] += 1
        # of the pot-winners who survived all 3 rounds, did they ride a playoff team?
        if best == 3:
            pot_decided += 1
            fps = [st[nm]["fp"] for nm in winners if st[nm]["fp"]]
            if fps and all(f not in finalists for f in fps):
                winners_via_playoff += 1
            if fps and all(f in finalists for f in fps):
                champ_is_finalist += 1
    n = len(sims)
    print(f"\n=== {label} ===")
    print(f"  {'player':8} {'EV':>6} {'solo':>7} {'stranded':>9}")
    res = {nm: agg[nm]["ev"] / n for nm in USED}
    for nm in sorted(USED, key=lambda x: -res[x]):
        print(f"  {nm:8} {res[nm]*100:5.1f}% {agg[nm]['solo']/n*100:6.1f}% "
              f"{agg[nm]['strand']/n*100:8.1f}%")
    print(f"  pot splits (>=2 winners): {split_ge2/n*100:.1f}%   avg winners {nwin_tot/n:.2f}")
    if playoff and pot_decided:
        print(f"  of decided pots, winners rode a PLAYOFF team: "
              f"{winners_via_playoff/pot_decided*100:.1f}%  (a finalist: "
              f"{champ_is_finalist/pot_decided*100:.1f}%)")
    return res


def main():
    d = data_io.load(DATA_DIR)
    teams, market, frp = d["teams"], d["market"], d["match"]
    theta = calibrate(teams, market, first_round_p=frp)
    _, model = fit_report(teams, theta, market, first_round_p=frp)
    ctx = Context(teams, theta, market, model)
    p = make_p(theta)
    sims = simulate_many(teams, theta, N_SIMS, seed=SEED, first_round_p=frp)
    print(f"QF picks locked: Huw=England, rest=Spain. ({N_SIMS} sims). Fair share 16.7%")
    a = evaluate(ctx, sims, False, p, "CURRENT RULES (final = 2 teams)")
    b = evaluate(ctx, sims, True, p, "PROPOSED (final round = final + 3rd/4th playoff)")
    print("\n  Change in EV:")
    for nm in sorted(USED, key=lambda x: -(b[x] - a[x])):
        print(f"    {nm:8} {a[nm]*100:5.1f}% -> {b[nm]*100:5.1f}%   ({(b[nm]-a[nm])*100:+.1f}pp)")


if __name__ == "__main__":
    main()
