"""EV analysis of the R16 pick against the real surviving field.

    python ev_run.py

Models the 8 survivors (with their R32 used-teams) as rivals and asks: for a
focal player choosing among candidate R16 picks, what's the expected share of
the pot? Run under a sharp field (everyone converges) and a looser one.
"""
import os

from lms import data_io
from lms.bracket import reach_markers
from lms.calibrate import calibrate, fit_report
from lms.ev import evaluate_pick
from lms.simulate import simulate_many
from lms.strategy import Context

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
N_SIMS = 20000
SEED = 4242

# The 8 R16 survivors and the team each already used in the R32 (can't repick).
SURVIVORS = [
    {"name": "Andy W", "used": ["Argentina"]},
    {"name": "Matty", "used": ["Argentina"]},
    {"name": "Hasan", "used": ["USA"]},
    {"name": "Huw", "used": ["USA"]},
    {"name": "Conrad", "used": ["England"]},
    {"name": "Andrea", "used": ["England"]},
    {"name": "Malley", "used": ["Belgium"]},
    {"name": "Mr T", "used": ["Egypt"]},
]

CANDIDATES = ["Morocco", "Brazil", "Colombia", None]  # None = play sharp (likely Morocco)


def main():
    d = data_io.load(DATA_DIR)
    teams, market = d["teams"], d["market"]
    theta = calibrate(teams, market)
    _, model = fit_report(teams, theta, market)
    ctx = Context(teams, theta, market, model)
    sims = simulate_many(teams, theta, N_SIMS, seed=SEED, first_round_p=d["match"])

    em = reach_markers(teams, theta)
    print(f"Field: {len(SURVIVORS)} survivors + 1 focal = {len(SURVIVORS) + 1} players. "
          f"Fair share = {1 / (len(SURVIVORS) + 1) * 100:.1f}% of pot.")
    print(f"Model reach-final: France {em['reach_final']['France']*100:.0f}%, "
          f"Argentina {em['reach_final']['Argentina']*100:.0f}%\n")

    for temp, label in ((0.0, "SHARP field (rivals all pile onto best harvest)"),
                        (0.05, "SEMI-sharp field (some spread)"),
                        (0.15, "LOOSE field (well spread)")):
        print(f"--- {label} ---")
        print(f"{'focal R16 pick':16}  {'EV (pot%)':>9}  {'solo win':>8}  "
              f"{'shared':>7}  {'out-behind':>10}")
        rows = []
        for c in CANDIDATES:
            r = evaluate_pick(ctx, sims, SURVIVORS, focal_used=[], r16_pick=c, temp=temp)
            rows.append(r)
        for r in sorted(rows, key=lambda r: -r["ev"]):
            print(f"{r['pick']:16}  {r['ev']*100:8.2f}%  {r['p_solo']*100:7.1f}%  "
                  f"{r['p_shared']*100:6.1f}%  {r['p_out_behind']*100:9.1f}%")
        print()

    print("EV = expected share of pot. 'out-behind' = focal eliminated while a rival")
    print("survives further (the cost of a lone contrarian bust).")


if __name__ == "__main__":
    main()
