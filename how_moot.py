"""How likely is the final-round rule change to matter AT ALL?

It only binds if >=2 players are still alive when the final round arrives. If one
man is left standing at the QF or the SF, he's declared the winner and the whole
argument is academic.

Implements the REAL rules:
  * a player is eliminated if their pick loses (or they can't pick),
  * UNLESS no active player picked a winner that round -> everyone continues,
  * if exactly one player remains, the game is over and he wins.
    python how_moot.py
"""
import os
import random

from lms import data_io
from lms.calibrate import calibrate, fit_report
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


def penalize(values, pen):
    if "Argentina" not in values or pen <= 0:
        return values
    v = {t: row[:] for t, row in values.items()}
    v["Argentina"] = [x - pen for x in v["Argentina"]]
    return v


def run(ctx, sim, rng):
    """Play QF and SF under the real rules. Return (settled_round, n_alive_entering_final)."""
    active = set(USED)
    used = {nm: set(USED[nm]) for nm in USED}
    for ri, rnd in enumerate(["QF", "SF"]):
        if len(active) <= 1:
            return rnd, len(active)          # already settled before this round
        parts = participants(sim, rnd)
        if ri > 0:
            vals, kk = round_values(ctx, parts)
            herd = penalize(vals, ARG_PEN)
        picks = {}
        for nm in sorted(active):
            legal = [t for t in parts if t not in used[nm]]
            if not legal:
                picks[nm] = None             # stranded == no pick
                continue
            if ri == 0:
                pick = QF_PICK[nm] if QF_PICK[nm] in legal else legal[0]
            else:
                v = herd if nm != "Huw" else penalize(vals, 0.0)
                pick = assignment_pick(v, kk, legal, rng, TEMP)
            picks[nm] = pick
            used[nm].add(pick)
        won = {nm: (picks[nm] is not None
                    and winner_of_match_containing(sim, rnd, picks[nm]) == picks[nm])
               for nm in active}
        if any(won.values()):                # normal: losers go out
            active = {nm for nm in active if won[nm]}
        # else: ALL picked losers -> nobody eliminated, everyone continues
        if len(active) == 1:
            return rnd, 1                    # last man standing -> game over
    return "Final", len(active)


def main():
    d = data_io.load(DATA_DIR)
    teams, market, frp = d["teams"], d["market"], d["match"]
    theta = calibrate(teams, market, first_round_p=frp)
    _, model = fit_report(teams, theta, market, first_round_p=frp)
    ctx = Context(teams, theta, market, model)
    sims = simulate_many(teams, theta, N_SIMS, seed=SEED, first_round_p=frp)
    rng = random.Random(SEED)

    settled_qf = settled_sf = reach_final_multi = reach_final_solo = 0
    # conditional on Belgium winning tonight
    bel_n = bel_qf = bel_sf = bel_multi = 0
    for sim in sims:
        spain_won = winner_of_match_containing(sim, "QF", "Spain") == "Spain"
        r, n = run(ctx, sim, rng)
        if r == "QF" or (r == "SF" and n == 1):
            pass
        if r == "QF":
            settled_qf += 1
        elif r == "SF":
            settled_sf += 1
        else:
            if n >= 2:
                reach_final_multi += 1
            else:
                reach_final_solo += 1
        if not spain_won:
            bel_n += 1
            if r == "QF":
                bel_qf += 1
            elif r == "SF":
                bel_sf += 1
            elif n >= 2:
                bel_multi += 1
    n = len(sims)
    print(f"Real rules, actual picks (Huw=England, rest=Spain). {n} sims.\n")
    print("Where does the pool actually get SETTLED?")
    print(f"  one man standing after the QF ....... {settled_qf/n*100:5.1f}%  (rule change MOOT)")
    print(f"  one man standing after the SF ....... {settled_sf/n*100:5.1f}%  (rule change MOOT)")
    print(f"  reach the final round, 1 alive ...... {reach_final_solo/n*100:5.1f}%  (rule change MOOT)")
    print(f"  reach the final round, 2+ alive ..... {reach_final_multi/n*100:5.1f}%  <-- ONLY here does it bind")
    moot = (settled_qf + settled_sf + reach_final_solo) / n
    print(f"\n  => the rule change is IRRELEVANT in {moot*100:.1f}% of worlds.")
    print(f"     it only changes anything in {reach_final_multi/n*100:.1f}%.")
    if bel_n:
        print(f"\nCONDITIONAL on Belgium beating Spain tonight (n={bel_n}, {bel_n/n*100:.1f}% of worlds):")
        print(f"  settled at the QF (Huw wins) ....... {bel_qf/bel_n*100:5.1f}%")
        print(f"  settled at the SF ................. {bel_sf/bel_n*100:5.1f}%")
        print(f"  final round with 2+ alive ......... {bel_multi/bel_n*100:5.1f}%")


if __name__ == "__main__":
    main()
