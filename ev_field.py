"""Current EV standings — QUARTER-FINALS (clean full round, 8 teams).
All 6 survivors are through and now face a QF pick. The save-aware assignment
policy chooses each player's QF/SF/Final plan from their legal (unused) teams.
    python ev_field.py
"""
import itertools
import os

from lms import data_io
from lms.calibrate import calibrate, fit_report
from lms.ev import evaluate_field, round_values
from lms.simulate import simulate_many
from lms.strategy import Context

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
N_SIMS = 40000
SEED = 909

# All 6 alive and through to the QF. `used` = full history (R32 + R16); no QF
# pick made yet, so r16=None -> the policy picks their QF team. Burned teams that
# are STILL ALIVE (Morocco, Argentina) are the ones that actually constrain.
FIELD = [
    {"name": "Matty",  "used": ["Argentina", "Morocco"], "r16": None},
    {"name": "Huw",    "used": ["USA", "Morocco"],       "r16": None},
    {"name": "Conrad", "used": ["England", "Morocco"],   "r16": None},
    {"name": "Andrea", "used": ["England", "Morocco"],   "r16": None},
    {"name": "Malley", "used": ["Belgium", "Morocco"],   "r16": None},
    {"name": "Hasan",  "used": ["USA", "Argentina"],     "r16": None},
]
ROUND_LABELS = ["QF", "SF", "Final"]


def best_plan(values, k_rounds, legal):
    """Best assignment of distinct legal teams to the remaining rounds
    (QF, SF, Final) maximising total log-emerge value. Returns (teams, logval)."""
    legal = [t for t in legal if t in values]
    if len(legal) < k_rounds:
        return None, None
    best_val, best_assign = -1e18, None
    for combo in itertools.permutations(legal, k_rounds):
        v = sum(values[combo[k]][k] for k in range(k_rounds))
        if v > best_val:
            best_val, best_assign = v, combo
    return best_assign, best_val


def main():
    d = data_io.load(DATA_DIR)
    teams, market, frp = d["teams"], d["market"], d["match"]
    theta = calibrate(teams, market, first_round_p=frp)
    errs, model = fit_report(teams, theta, market, first_round_p=frp)
    ctx = Context(teams, theta, market, model)
    sims = simulate_many(teams, theta, N_SIMS, seed=SEED, first_round_p=frp)

    print("Calibration fit (mean abs err): "
          + "  ".join(f"{k}={v*100:.2f}pp" for k, v in errs.items()))

    # ---- recommended QF plan per player (deterministic, on calibrated bracket) ----
    values, k_rounds = round_values(ctx, teams)
    print("\nRecommended plan (save-aware assignment, teams reserved to latest round):")
    print(f"{'player':9} {'burned(alive)':14} {'QF pick':11} plan (QF -> SF -> Final)")
    print("-" * 72)
    alive_set = set(teams)
    for p in FIELD:
        used = set(p["used"])
        legal = [t for t in teams if t not in used]
        plan, _ = best_plan(values, k_rounds, legal)
        burned_alive = ",".join(t for t in p["used"] if t in alive_set) or "-"
        qf = plan[0] if plan else "STRANDED"
        plan_str = " -> ".join(plan) if plan else "-"
        print(f"{p['name']:9} {burned_alive:14} {qf:11} {plan_str}")

    # ---- Monte-Carlo EV standings ----
    n = len(FIELD)
    rows = evaluate_field(ctx, sims, FIELD, policy="assign", temp=0.12)
    print(f"\n{n} players alive. Fair share = {100/n:.1f}% of pot.")
    print("(save-aware assignment continuation, moderate rival plan-divergence)\n")
    print(f"{'player':9} {'burned(alive)':14} {'survive QF':>10}  {'EV':>6}  {'solo':>6}")
    print("-" * 54)
    burned = {p["name"]: ",".join(t for t in p["used"] if t in alive_set) or "-"
              for p in FIELD}
    for r in sorted(rows, key=lambda r: -r["ev"]):
        print(f"{r['name']:9} {burned[r['name']]:14} "
              f"{r['p_survive_r16']*100:8.1f}%  {r['ev']*100:4.1f}%  "
              f"{r['p_solo_win']*100:4.1f}%")


if __name__ == "__main__":
    main()
