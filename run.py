"""End-to-end driver: load data -> calibrate strengths -> Monte-Carlo ->
compare pick policies. Run:  python run.py
"""
import os
import sys

from lms import data_io
from lms.bracket import reach_markers
from lms.calibrate import calibrate, fit_report
from lms.evaluate import evaluate, format_table
from lms.simulate import simulate_many
from lms.strategy import Context, POLICIES

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
N_SIMS = 20000
SEED = 12345


def main():
    d = data_io.load(DATA_DIR)
    teams, market = d["teams"], d["market"]

    print(f"Loaded {len(teams)} teams. Current round: {d['current_round']}\n")

    print("Calibrating team strengths to market markers ...")
    theta = calibrate(teams, market)
    errs, model = fit_report(teams, theta, market)
    print("  mean abs error vs market:  " +
          "  ".join(f"{k}={v*100:.2f}pp" for k, v in errs.items()))

    # sanity: exact reach-probs must sum to known totals
    em = reach_markers(teams, theta)
    print("  reach-prob sums (should be win=1, reach_final=2, reach_semi=4): "
          f"{sum(em['win'].values()):.3f}, {sum(em['reach_final'].values()):.3f}, "
          f"{sum(em['reach_semi'].values()):.3f}")

    top = sorted(em["win"].items(), key=lambda kv: -kv[1])[:6]
    print("  top title chances: " + ", ".join(f"{t} {p*100:.1f}%" for t, p in top))

    print(f"\nRunning {N_SIMS} Monte-Carlo tournaments ...")
    sims = simulate_many(teams, theta, N_SIMS, seed=SEED)

    ctx = Context(teams, theta, market, model)
    results = [evaluate(name, sims, ctx) for name in POLICIES]

    print("\nStrategy comparison (probability of surviving through each round):\n")
    print(format_table(results))
    print("\n  5/5      = outright win (subject to share rules, opponents TBD)")
    print("  stranded = reached a round with no legal pick (final-with-no-team risk)")


if __name__ == "__main__":
    sys.exit(main())
