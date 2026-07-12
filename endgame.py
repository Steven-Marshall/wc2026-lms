"""EXACT solver for the endgame. Two rounds left:

  SEMI   : France v Spain  |  England v Argentina   (pick 1, must win)
  FINAL  : the FINAL (2 semi winners) AND the 3rd/4th PLAYOFF (2 semi losers)
           are played in the SAME round -> all four teams are playing. Pick any
           unused one; you survive if it wins ITS match.

Real rules applied:
  * pick loses -> out, UNLESS no active player picked a winner -> all continue
  * exactly one player left -> he is declared the winner
  * tournament out of rounds -> remaining players are joint winners (split)

No Monte Carlo: 4 semi outcomes x 4 final-round outcomes = 16 worlds, enumerated
exactly with probabilities from the fitted strengths.
    python endgame.py
"""
import itertools
import os
from collections import defaultdict

from lms import data_io
from lms.bracket import make_p
from lms.calibrate import calibrate

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

SEMI1 = ("France", "Spain")
SEMI2 = ("England", "Argentina")
FOUR = ["France", "Spain", "England", "Argentina"]

BURNED = {
    "Huw":    {"England"},
    "Malley": {"Spain"},
    "Matty":  {"Spain", "Argentina"},
    "Hasan":  {"Spain", "Argentina"},
    "Conrad": {"Spain", "England"},
    "Andrea": {"Spain", "England"},
}
PLAYERS = list(BURNED)
AVAIL = {nm: [t for t in FOUR if t not in BURNED[nm]] for nm in PLAYERS}


def build_worlds(p):
    """Yield (w1, w2, l1, l2, final_winner, playoff_winner, probability)."""
    for w1 in SEMI1:
        l1 = SEMI1[0] if w1 == SEMI1[1] else SEMI1[1]
        p1 = p(w1, l1)
        for w2 in SEMI2:
            l2 = SEMI2[0] if w2 == SEMI2[1] else SEMI2[1]
            p2 = p(w2, l2)
            for fw in (w1, w2):                     # who wins the FINAL
                fl = w2 if fw == w1 else w1
                pf = p(fw, fl)
                for pw in (l1, l2):                 # who wins the PLAYOFF
                    pl = l2 if pw == l1 else l1
                    pp = p(pw, pl)
                    yield w1, w2, l1, l2, fw, pw, p1 * p2 * pf * pp


def evaluate(worlds, semi, final):
    """semi: {player: team}. final: {player: {(w1,w2): team}} (or {player: team}).
    Returns exact EV (expected pot share) per player."""
    ev = defaultdict(float)
    for w1, w2, l1, l2, fw, pw, prob in worlds:
        winners_semi = {w1, w2}
        alive = [nm for nm in PLAYERS if semi[nm] in winners_semi]
        if not alive:                       # nobody picked a winner -> all continue
            alive = list(PLAYERS)
        if len(alive) == 1:                 # last man standing -> game over, he wins
            ev[alive[0]] += prob
            continue
        round_winners = {fw, pw}
        survivors = []
        for nm in alive:
            f = final[nm]
            pick = f[(w1, w2)] if isinstance(f, dict) else f
            if pick == semi[nm] or pick not in AVAIL[nm]:
                raise ValueError(f"{nm}: illegal final pick {pick}")
            if pick in round_winners:
                survivors.append(nm)
        if not survivors:                   # all picked losers -> all continue
            survivors = alive               # ...but no rounds left -> joint winners
        share = prob / len(survivors)
        for nm in survivors:
            ev[nm] += share
    return dict(ev)


def best_final(nm, semi_pick):
    """A player's remaining team(s) after the semi."""
    return [t for t in AVAIL[nm] if t != semi_pick]


def show(title, ev, semi, note=""):
    print(f"\n=== {title} ===  {note}")
    tot = sum(ev.values())
    for nm in sorted(PLAYERS, key=lambda x: -ev.get(x, 0)):
        print(f"  {nm:8} semi={semi[nm]:10} EV={ev.get(nm, 0)*100:5.1f}%")
    print(f"  (total {tot*100:.1f}%)")


def main():
    d = data_io.load(DATA_DIR)
    theta = calibrate(d["teams"], d["market"], first_round_p=d["match"])
    p = make_p(theta)
    worlds = list(build_worlds(p))
    print(f"Exact endgame. {len(worlds)} worlds, total prob "
          f"{sum(w[-1] for w in worlds):.6f}")

    # --- France's value as a final-round asset, whatever happens in the semi ---
    pf_final = sum(prob for *_, fw, pw, prob in
                   [(w) for w in worlds] if False)  # placeholder
    win_if = defaultdict(float)
    tot = defaultdict(float)
    for w1, w2, l1, l2, fw, pw, prob in worlds:
        for t in FOUR:
            tot[t] += prob
            if t in (fw, pw):
                win_if[t] += prob
    print("\nP(team wins its FINAL-ROUND match — final or playoff):")
    for t in FOUR:
        print(f"  {t:10} {win_if[t]/tot[t]*100:5.1f}%")

    # --- BASELINE: everyone saves France, spends their other team in the semi ---
    semi = {"Matty": "England", "Hasan": "England",
            "Conrad": "Argentina", "Andrea": "Argentina",
            "Huw": "Argentina", "Malley": "Argentina"}
    final = {nm: "France" for nm in PLAYERS}
    ev = evaluate(worlds, semi, final)
    show("BASELINE: all hold France, all play France in the final round", ev, semi,
         "<- the final round is a NO-OP")

    # --- the same, but ONE player defects in the final round ---
    print("\n\n--- What if one player does NOT play France in the final round? ---")
    for nm in PLAYERS:
        opts = best_final(nm, semi[nm])
        for alt in opts:
            if alt == "France":
                continue
            f2 = dict(final)
            f2[nm] = alt
            ev2 = evaluate(worlds, semi, f2)
            print(f"  {nm:8} plays {alt:10} in the final round instead of France: "
                  f"{ev.get(nm,0)*100:5.1f}% -> {ev2[nm]*100:5.1f}%   "
                  f"(others now ~{ev2['Matty' if nm!='Matty' else 'Hasan']*100:.1f}%)")


if __name__ == "__main__":
    main()
