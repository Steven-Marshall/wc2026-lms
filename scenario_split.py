"""What does a 2/2/2 split look like — two hold Spain, two hold France, two hold
England? Runs the full field with every player on a fixed lane, two allocations
(swapped) to separate 'lane effect' from 'who is in it'.
    python scenario_split.py
"""
import os

from lms import data_io
from lms.calibrate import calibrate, fit_report
from lms.simulate import simulate_many
from lms.strategy import Context
from ev_deviation import (USED, NAMES, run_scenario, consensus, keep_spain,
                          hold_england, DATA_DIR, N_SIMS, SEED)

LANE_FN = {"Spain": keep_spain, "France": consensus, "England": hold_england}


def alloc_to_fixed(alloc):
    return {nm: LANE_FN[lane](nm) for nm, lane in alloc.items()}


def show_split(title, ctx, sims, alloc):
    res = run_scenario(ctx, sims, alloc_to_fixed(alloc))
    print(f"\n{title}")
    for nm in sorted(NAMES, key=lambda x: -res[x]["ev"]):
        r = res[nm]
        print(f"  {nm:8} [{alloc[nm]:7}] EV={r['ev']*100:5.1f}%  "
              f"solo={r['solo']*100:4.1f}%  inmoney={r['money']*100:4.1f}%")
    # lane averages
    lanes = {}
    for nm, lane in alloc.items():
        lanes.setdefault(lane, []).append(res[nm]["ev"])
    avg = {L: sum(v) / len(v) for L, v in lanes.items()}
    print("  lane avg EV: " + "   ".join(f"{L}={avg[L]*100:.1f}%" for L in ["Spain", "France", "England"]))


def main():
    d = data_io.load(DATA_DIR)
    teams, market, frp = d["teams"], d["market"], d["match"]
    theta = calibrate(teams, market, first_round_p=frp)
    _, model = fit_report(teams, theta, market, first_round_p=frp)
    ctx = Context(teams, theta, market, model)
    sims = simulate_many(teams, theta, N_SIMS, seed=SEED, first_round_p=frp)
    print(f"2/2/2 split ({N_SIMS} sims). Fair share = 16.7%.")

    # England-holders must be from {Matty,Huw,Malley,Hasan}; Conrad/Andrea can't.
    # Allocation A: flexible pair on Spain, forced pair on France, Arg-burned on England.
    show_split("=== A: Spain=Huw,Malley | France=Conrad,Andrea | England=Matty,Hasan ===",
               ctx, sims,
               {"Huw": "Spain", "Malley": "Spain", "Conrad": "France",
                "Andrea": "France", "Matty": "England", "Hasan": "England"})

    # Allocation B: swap the lanes around (England-capable pair now on England).
    show_split("=== B: Spain=Conrad,Andrea | France=Matty,Hasan | England=Huw,Malley ===",
               ctx, sims,
               {"Conrad": "Spain", "Andrea": "Spain", "Matty": "France",
                "Hasan": "France", "Huw": "England", "Malley": "England"})


if __name__ == "__main__":
    main()
