"""Scenario engine: give any subset of players a FIXED plan (QF/SF/Final teams);
everyone else plays the save-aware assignment policy (the "consensus" field).
Reports EV / solo-win / in-money for all 6, so we can price contrarian holds
(keep-Spain, hold-England) AND see how they crowd each other.
    python ev_deviation.py
"""
import os
import random

from lms import data_io
from lms.calibrate import calibrate, fit_report
from lms.ev import round_values, assignment_pick
from lms.simulate import simulate_many, participants, winner_of_match_containing
from lms.strategy import Context

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
N_SIMS = 30000
SEED = 909
TEMP = 0.12
ROUNDS = ["QF", "SF", "Final"]

# Full history (R32+R16). Morocco/Argentina are the burns still alive.
USED = {
    "Matty":  ["Argentina", "Morocco"],   # can't pick Arg or Morocco; CAN hold England
    "Huw":    ["USA", "Morocco"],         # flexible; CAN hold England
    "Conrad": ["England", "Morocco"],     # burned England -> CANNOT hold it
    "Andrea": ["England", "Morocco"],     # burned England -> CANNOT hold it
    "Malley": ["Belgium", "Morocco"],     # flexible; CAN hold England
    "Hasan":  ["USA", "Argentina"],       # can't pick Arg; CAN hold England
}
NAMES = list(USED)

# Named plans. H1 disposable = France or Spain (same half, only one survives).
def consensus(name):
    # spend Spain (QF), a half-2 team (SF), hold France (Final)
    sf = "England" if "Argentina" in USED[name] else "Argentina"
    return ["Spain", sf, "France"]

def keep_spain(name):
    sf = "England" if "Argentina" in USED[name] else "Argentina"
    return ["France", sf, "Spain"]

def hold_england(name):
    # spend Spain (QF), ride France through the H1 semi (SF), hold England (Final)
    return ["Spain", "France", "England"]


def play_plan(ctx, sim, used0, plan):
    used = set(used0)
    n = 0
    for i, rnd in enumerate(ROUNDS):
        parts = participants(sim, rnd)
        legal = [t for t in parts if t not in used]
        if not legal:
            break
        want = plan[i]
        pick = want if want in legal else max(legal, key=lambda t: ctx.p_win_match(sim, rnd, t))
        used.add(pick)
        if winner_of_match_containing(sim, rnd, pick) == pick:
            n += 1
        else:
            break
    return n


def run_scenario(ctx, sims, fixed):
    """fixed: {name: plan}. Players not in `fixed` play assignment policy (temp)."""
    rng = random.Random(SEED)
    agg = {nm: {"ev": 0.0, "solo": 0, "money": 0} for nm in NAMES}
    policy_names = [nm for nm in NAMES if nm not in fixed]
    for sim in sims:
        res = {}
        # policy players share round_values per round
        pstate = {nm: {"used": set(USED[nm]), "alive": True, "n": 0} for nm in policy_names}
        for rnd in ROUNDS:
            parts = participants(sim, rnd)
            if policy_names:
                vals, kk = round_values(ctx, parts)
            for nm in policy_names:
                st = pstate[nm]
                if not st["alive"]:
                    continue
                legal = [t for t in parts if t not in st["used"]]
                if not legal:
                    st["alive"] = False
                    continue
                pick = assignment_pick(vals, kk, legal, rng, TEMP)
                st["used"].add(pick)
                if winner_of_match_containing(sim, rnd, pick) == pick:
                    st["n"] += 1
                else:
                    st["alive"] = False
        for nm in policy_names:
            res[nm] = pstate[nm]["n"]
        for nm, plan in fixed.items():
            res[nm] = play_plan(ctx, sim, USED[nm], plan)
        best = max(res.values())
        winners = [nm for nm, k in res.items() if k == best]
        for nm in NAMES:
            if res[nm] == best:
                agg[nm]["ev"] += 1.0 / len(winners)
                agg[nm]["money"] += 1
                if len(winners) == 1:
                    agg[nm]["solo"] += 1
    n = len(sims)
    return {nm: {"ev": a["ev"] / n, "solo": a["solo"] / n, "money": a["money"] / n}
            for nm, a in agg.items()}


def show(title, res, note=""):
    print(f"\n{title}  {note}")
    for nm in sorted(NAMES, key=lambda x: -res[x]["ev"]):
        r = res[nm]
        print(f"  {nm:8} EV={r['ev']*100:5.1f}%  solo={r['solo']*100:4.1f}%  "
              f"inmoney={r['money']*100:4.1f}%")


def main():
    d = data_io.load(DATA_DIR)
    teams, market, frp = d["teams"], d["market"], d["match"]
    theta = calibrate(teams, market, first_round_p=frp)
    _, model = fit_report(teams, theta, market, first_round_p=frp)
    ctx = Context(teams, theta, market, model)
    sims = simulate_many(teams, theta, N_SIMS, seed=SEED, first_round_p=frp)
    print(f"Scenarios ({N_SIMS} sims, temp={TEMP}). Fair share = 16.7%.")

    # --- per-player single-deviation pricing (rest play consensus policy) ---
    print("\n=== Single deviation: this player deviates, other five stay consensus ===")
    print(f"{'player':8} {'consensus':>10} {'keepSpain':>10} {'holdEng':>10}")
    can_eng = [nm for nm in NAMES if "England" not in USED[nm]]
    for nm in NAMES:
        c = run_scenario(ctx, sims, {nm: consensus(nm)})[nm]["ev"]
        ks = run_scenario(ctx, sims, {nm: keep_spain(nm)})[nm]["ev"]
        he = run_scenario(ctx, sims, {nm: hold_england(nm)})[nm]["ev"] if nm in can_eng else None
        he_s = f"{he*100:9.1f}%" if he is not None else "     n/a "
        print(f"{nm:8} {c*100:9.1f}% {ks*100:9.1f}% {he_s}")

    # --- realistic field: a couple of patriots hold England ---
    show("=== Baseline: everyone consensus ===",
         run_scenario(ctx, sims, {}))
    show("=== Two patriots (Matty, Malley) hold England ===",
         run_scenario(ctx, sims, {"Matty": hold_england("Matty"),
                                  "Malley": hold_england("Malley")}))
    show("=== Patriots hold England + Huw keeps Spain (the sharp lonely lane) ===",
         run_scenario(ctx, sims, {"Matty": hold_england("Matty"),
                                  "Malley": hold_england("Malley"),
                                  "Huw": keep_spain("Huw")}))


if __name__ == "__main__":
    main()
