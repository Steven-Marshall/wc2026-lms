"""Current EV standings — R16 half played (Morocco/France/Norway/England through;
Argentina, USA, Spain, Colombia ties pending). Decided ties are locked; pending
ties + QF/SF/Final simulate from the amended odds.
    python ev_field.py
"""
import os

from lms import data_io
from lms.calibrate import calibrate, fit_report
from lms.ev import evaluate_field
from lms.simulate import simulate_many
from lms.strategy import Context

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
N_SIMS = 40000
SEED = 909

# The 7 players still alive. used = R32 team; r16 = their R16 pick.
FIELD = [
    {"name": "Matty",  "used": ["Argentina"], "r16": "Morocco"},
    {"name": "Huw",    "used": ["USA"],       "r16": "Morocco"},
    {"name": "Conrad", "used": ["England"],   "r16": "Morocco"},
    {"name": "Andrea", "used": ["England"],   "r16": "Morocco"},
    {"name": "Malley", "used": ["Belgium"],   "r16": "Morocco"},
    {"name": "Hasan",  "used": ["USA"],       "r16": "Argentina"},  # pending v Egypt
    {"name": "Mr T",   "used": ["Egypt"],     "r16": "USA"},        # pending v Belgium
]


def main():
    d = data_io.load(DATA_DIR)
    teams, market, frp = d["teams"], d["market"], d["match"]
    theta = calibrate(teams, market, first_round_p=frp)
    errs, model = fit_report(teams, theta, market, first_round_p=frp)
    ctx = Context(teams, theta, market, model)
    sims = simulate_many(teams, theta, N_SIMS, seed=SEED, first_round_p=frp)

    print(f"Calibration fit (mean abs err): "
          + "  ".join(f"{k}={v*100:.2f}pp" for k, v in errs.items()))
    n = len(FIELD)
    spent = {p["name"]: p["used"][0] for p in FIELD}
    # save-aware assignment continuation, with moderate plan-divergence (real
    # rivals don't all run the identical optimal plan).
    rows = evaluate_field(ctx, sims, FIELD, policy="assign", temp=0.12)
    print(f"\n{n} players still alive. Fair share = {100/n:.1f}% of pot.")
    print("(save-aware assignment policy, moderate rival plan-divergence)\n")
    print(f"{'player':9} {'R16 pick':10} {'spent':10} {'survive R16':>11}  {'EV':>7}")
    print("-" * 55)
    for r in sorted(rows, key=lambda r: -r["ev"]):
        print(f"{r['name']:9} {r['r16']:10} {spent[r['name']]:10} "
              f"{r['p_survive_r16']*100:9.1f}%  {r['ev']*100:5.1f}%")


if __name__ == "__main__":
    main()
