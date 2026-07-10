"""What happens to the pool if Morocco (the team ALL SIX of us burned) storms to
the final? Runs a realistic fixed field and reports the outcome mix overall and
CONDITIONED on Morocco reaching the final.
    python morocco_chaos.py
"""
import os

from lms import data_io
from lms.calibrate import calibrate, fit_report
from lms.simulate import simulate_many, participants, winner_of_match_containing
from lms.strategy import Context

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
N_SIMS = 60000
SEED = 909
ROUNDS = ["QF", "SF", "Final"]

USED = {
    "Huw":    ["USA", "Morocco"],
    "Matty":  ["Argentina", "Morocco"],
    "Malley": ["Belgium", "Morocco"],
    "Hasan":  ["USA", "Argentina"],
    "Conrad": ["England", "Morocco"],
    "Andrea": ["England", "Morocco"],
}
# Realistic field: 2 hold England (patriots), 4 hold France; Conrad/Andrea forced
# onto the Argentina semi vehicle (they burned England).
PLAN = {
    "Huw":    ["Spain", "France", "England"],      # patriot (hold England)
    "Matty":  ["Spain", "France", "England"],      # patriot (hold England)
    "Malley": ["Spain", "England", "France"],      # safe (hold France)
    "Hasan":  ["Spain", "England", "France"],      # safe (hold France)
    "Conrad": ["Spain", "Argentina", "France"],    # burnt-England (ride Argentina)
    "Andrea": ["Spain", "Argentina", "France"],    # burnt-England (ride Argentina)
}


def run_player(ctx, sim, used0, plan):
    """Return (n_rounds_won, final_pick_or_None, stranded_at_final_bool)."""
    used = set(used0)
    n = 0
    final_pick = None
    stranded_final = False
    for i, rnd in enumerate(ROUNDS):
        parts = participants(sim, rnd)
        legal = [t for t in parts if t not in used]
        if not legal:
            if rnd == "Final":
                stranded_final = True      # reached the final, no legal team
            break
        want = plan[i]
        pick = want if want in legal else max(legal, key=lambda t: ctx.p_win_match(sim, rnd, t))
        if rnd == "Final":
            final_pick = pick
        used.add(pick)
        if winner_of_match_containing(sim, rnd, pick) == pick:
            n += 1
        else:
            break
    return n, final_pick, stranded_final


def classify(sim, ctx):
    res = {nm: run_player(ctx, sim, USED[nm], PLAN[nm]) for nm in USED}
    ns = {nm: r[0] for nm, r in res.items()}
    best = max(ns.values())
    winners = [nm for nm, n in ns.items() if n == best]
    reached = [nm for nm, n in ns.items() if n >= 2]
    champions = [nm for nm, n in ns.items() if n == 3]
    if champions:
        bucket = "champion_at_final"
    elif best == 2:
        bucket = "stranded_split"      # all finalists stuck at 2 (lost/stranded)
    elif best == 1:
        bucket = "semi_cull_split"     # furthest only won the QF
    else:
        bucket = "qf_wipeout"
    semi_winner = (len(reached) == 1 and best >= 2)   # sole survivor into the final
    return {"bucket": bucket, "winners": winners, "n_win": len(winners),
            "reached": len(reached), "semi_winner": semi_winner,
            "won_via_arg": bool(champions) and all(res[w][1] == "Argentina" for w in winners),
            "solo": len(winners) == 1}


def summarise(rows, label):
    n = len(rows)
    if n == 0:
        print(f"\n{label}: no sims"); return
    from collections import Counter
    buckets = Counter(r["bucket"] for r in rows)
    solo = sum(r["solo"] for r in rows)
    semiw = sum(r["semi_winner"] for r in rows)
    arg = sum(r["won_via_arg"] for r in rows)
    avg_split = sum(r["n_win"] for r in rows) / n
    avg_split_when_shared = (sum(r["n_win"] for r in rows if r["n_win"] > 1)
                             / max(1, sum(1 for r in rows if r["n_win"] > 1)))
    print(f"\n{label}  (n={n}, {100*n/N_SIMS:.1f}% of all sims)")
    print(f"  sole winner ....... {100*solo/n:5.1f}%")
    print(f"  shared / split .... {100*(n-solo)/n:5.1f}%   (avg {avg_split_when_shared:.1f} way when split)")
    print(f"  -- won in the semis (sole survivor into final): {100*semiw/n:5.1f}%")
    print(f"  -- won via holding Argentina .................: {100*arg/n:5.1f}%")
    print(f"  outcome type:")
    for b in ("champion_at_final", "stranded_split", "semi_cull_split", "qf_wipeout"):
        if buckets.get(b):
            print(f"     {b:20} {100*buckets[b]/n:5.1f}%")


def main():
    d = data_io.load(DATA_DIR)
    teams, market, frp = d["teams"], d["market"], d["match"]
    theta = calibrate(teams, market, first_round_p=frp)
    _, model = fit_report(teams, theta, market, first_round_p=frp)
    ctx = Context(teams, theta, market, model)
    sims = simulate_many(teams, theta, N_SIMS, seed=SEED, first_round_p=frp)
    print(f"Morocco-chaos pricing ({N_SIMS} sims). Field: 2 hold England, 4 hold "
          f"France (Conrad/Andrea ride Argentina).")

    allrows, mor_final, mor_arg_final = [], [], []
    for sim in sims:
        finalists = participants(sim, "Final")
        r = classify(sim, ctx)
        allrows.append(r)
        if "Morocco" in finalists:
            mor_final.append(r)
            if "Argentina" in finalists:
                mor_arg_final.append(r)

    summarise(allrows, "ALL worlds")
    summarise(mor_final, "MOROCCO reaches the final")
    summarise(mor_arg_final, "MOROCCO v ARGENTINA final (the nightmare)")


if __name__ == "__main__":
    main()
