"""Per-stage pick helper. Run once per round, after updating the data files to
the surviving teams + that round's odds.

    python pick.py --used England,Brazil

Prints every match in the live round with two signals:
  * P(win this match)        -- how safe the pick is right now
  * opportunity cost          -- how badly you'll want this team in a LATER round
                                 (reach-semi early on; reach-final once the QF
                                 arrives, when "reach-semi" just means winning
                                 this match).
The "harvest" score = P(win match) x (1 - opportunity cost): a near-certain win
from a team you were never going to need later. Used (already-picked) teams are
removed -- you can't repick them.
"""
import argparse
import os

from lms import data_io, jsonc, odds
from lms.bracket import ROUND_BY_SIZE, quadrant_of, reach_markers, round_pairs
from lms.calibrate import calibrate


def opportunity_marker(k, available):
    """Which deep-run marker is the right 'cost of using this team now'.
    Early rounds: reach-semi. From the QF down: reach-final (the teams you must
    save are the finalists). Falls back to whatever the bracket still supports."""
    preferred = "reach_semi" if k >= 16 else "reach_final"
    for m in (preferred, "reach_final", "reach_semi", "win"):
        if m in available:
            return m
    return "win"


def main():
    ap = argparse.ArgumentParser(description="Last-man-standing per-stage pick helper")
    ap.add_argument("--used", default="", help="comma-separated teams already picked")
    ap.add_argument("--data", default="data", help="data directory")
    args = ap.parse_args()
    used = {u.strip() for u in args.used.split(",") if u.strip()}

    d = data_io.load(args.data)
    teams = d["teams"]
    k = len(teams)
    rnd = ROUND_BY_SIZE.get(k, f"{k}-team round")

    theta = calibrate(teams, d["market"])
    em = reach_markers(teams, theta)
    opp = opportunity_marker(k, em)

    raw_match = jsonc.load(os.path.join(args.data, "markets.jsonc"))["match"]
    pairs = round_pairs(teams)
    mw = odds.match_probs(raw_match, pairs)

    def harvest(t):
        return mw[t] * (1.0 - em[opp].get(t, 0.0))

    print(f"\nRound: {rnd}  ({k} teams, {k // 2} matches)   "
          f"opportunity-cost signal: {opp}")
    if used:
        print(f"Cannot pick (already used): {', '.join(sorted(used))}")
    print()
    header = f"{'#':>2} Q  {'FAVOURITE':13}Pwin   {'opp-cost':>8}  harvest   vs {'underdog':13}"
    print(header)
    print("-" * len(header))

    candidates = []
    for i, (a, b) in enumerate(pairs):
        fav, dog = (a, b) if mw[a] >= mw[b] else (b, a)
        tag = ""
        if fav in used:
            tag = "  <- USED, must pick underdog or skip"
        else:
            candidates.append(fav)
        if dog not in used and dog != fav:
            candidates.append(dog)
        print(f"{i + 1:>2} {quadrant_of(i * 2)}  {fav:13}{mw[fav] * 100:3.0f}%   "
              f"{em[opp].get(fav, 0) * 100:6.0f}%  {harvest(fav):6.3f}   vs {dog:13}{tag}")

    pickable = [t for t in candidates if t not in used]
    pickable.sort(key=harvest, reverse=True)
    print()
    if not pickable:
        print("No legal pick left -- you are STRANDED this round.")
        return
    print("Recommended picks (highest harvest among available teams):")
    for t in pickable[:3]:
        print(f"   {t:13} Pwin={mw[t] * 100:.0f}%  {opp}={em[opp].get(t, 0) * 100:.0f}%  "
              f"harvest={harvest(t):.3f}")
    print(f"\n=> PICK: {pickable[0]}  (safest win among teams you won't need later)")


if __name__ == "__main__":
    main()
