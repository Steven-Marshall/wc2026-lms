# Last Man Standing — World Cup 2026 strategy explorer

A simulator for a knockout-stage Last-Man-Standing pool. From the **Round of 32**
you pick one team per round; the team must **win** to keep you alive; you may
**never repick** a team. Five rounds: **R32 → R16 → QF → SF → Final**.

### Our pool's specifics
- **~15 players** enter the knockout (started ~20; qualifying-stage upsets thinned it).
- **Reset at the last 32** — group-stage picks don't carry over, so everyone
  starts the knockout with an empty used-list (no team burn).
- **Single fixed pot.** It goes to whoever survives longest; split equally if
  several tie — both when several go 5/5 *and* when the last survivors all go out
  in the same round (co-elimination).
- **Pick history is public**, so you always know what every rival has burned.
  Each round's picks are **revealed simultaneously**, so you have no in-round
  foreknowledge — every round is a simultaneous-move game played against a
  *prediction* of rivals' picks (from their history + style), not their actual pick.

### The core insight the model is built around
Because you can't repick, and the only winner of the Final is the champion, an
**outright win forces you to "save" the eventual champion for the Final** and
correctly back the **runner-up** in the SF — plus three safe "harvest" wins
early. Working backwards: Final = champion, SF = runner-up, QF = a losing
semi-finalist, R16/R32 = safe-but-shallow filler. Reaching a round with no legal
team left = **stranded** (the "final-with-no-team" case); on its own that can
only pay if every other survivor also goes out in the same round.

## Quick start
```
python data/_generate_dummy.py   # (re)generate consistent DUMMY data
python run.py                     # calibrate -> Monte-Carlo -> compare strategies
python pick.py --used England,Brazil   # per-stage pick helper (the main tool)
python tests/test_odds.py         # sanity tests
```
Pure standard library — no pip installs needed.

## Per-stage workflow (what you actually do each round)
The engine is bracket-size agnostic (32 → 16 → 8 → 4 → 2). Each round:
1. Edit `data/bracket.jsonc` → the surviving teams, in bracket order.
2. Edit `data/markets.jsonc` → refreshed `win` / `reach_final` / `reach_semi`
   odds + that round's `match` prices. Markets that no longer exist (e.g.
   "reach semi" once you're *in* the semis) can be omitted — the loader and
   calibrator tolerate missing markers.
3. `python pick.py --used <every team you've already picked>`

`pick.py` prints every live match with two signals and a recommendation:
- **P(win this match)** — how safe the pick is right now.
- **opportunity cost** — how badly you'll want this team in a *later* round.
  Auto-switches by stage: **reach-semi** at R32/R16, then **reach-final** from
  the QF onward (where "reach-semi" just means winning this match). The header
  prints which signal it used.
- **harvest score = P(win match) × (1 − opportunity cost)** — a near-certain win
  from a team you were never going to need later. Used teams are removed; if all
  live teams are used it reports STRANDED.

### The "free option" / harvest principle
Every team you *don't* pick stays available for a later round, so spend each
round on a team whose future option value is ~zero: a heavy match favourite that
won't go deep anyway. Top-heavy quadrants (e.g. two strong teams sharing a
quadrant) *manufacture* ideal early picks — the safe also-rans sitting behind
them (they'll be knocked out soon, so using them costs you nothing). Never spend
a genuine semi-final contender early; those are the teams you're saving.

## Data format (`data/`)
- **`bracket.jsonc`** — teams in bracket/slot order. Matches are consecutive
  pairs; quadrant A = slots 0–7, B = 8–15, C = 16–23, D = 24–31; one team per
  quadrant reaches the semis. (Fewer teams in later rounds — must be a power of two.)
- **`markets.jsonc`** — decimal $1-stake prices. A value is either a firm price
  (`7.5`) or a back/lay spread (`[7.4, 7.6]`, we take the mid). **Prices need not
  sum to 100%** — overround is removed by normalising each market to its known
  total (win→1, reach_final→2, reach_semi→4, each match→1). Totals are
  stage-invariant (always 1 champion, 2 finalists, 4 semi-finalists).

Both files currently hold **dummy** data. Overwrite once the real R32 is set.

## How it works
1. **`lms/odds.py`** — decimal odds → vig-free probabilities.
2. **`lms/bracket.py`** — exact reach-probabilities for the bracket (also fills
   in reach-QF / reach-R16, which the markets don't quote). Works at any size.
3. **`lms/calibrate.py`** — fits one Bradley-Terry strength per team so the exact
   reach-probs match whichever market markers are available.
4. **`lms/simulate.py`** — Monte-Carlo: samples whole tournaments.
5. **`lms/strategy.py`** — pick policies + the no-repick / stranded rules.
6. **`lms/evaluate.py`** — survival distribution per policy.
7. **`pick.py`** — per-stage harvest table + recommendation (the day-to-day tool).

## Expected value & opponents (the late-game brain — DESIGNED, NOT BUILT)
Survival vs EV differ because of pot-sharing. Findings to implement when the
field thins (~QF/SF, down to a handful of players):

**Why EV is dormant early, decisive late.** With many players you'll share
regardless, and constraints start identical (reset) and diverge only slowly.
Separation needs *differing outcomes*, not differing picks — safe favourites
nearly all win together early, so you can't pull away from a 15-strong pack.
**So R32/R16 = pure survival (the harvest strategy, no opponent model needed);**
EV switches on once the field is small enough to be alone at the front.

**Lever 1 — champion-lane steering (history-based, robust to simultaneous
reveal).** To win outright you must ride the eventual champion through the Final.
A rival who has *burned* a contender can't take it — so as the field narrows,
choose which contender to **save** by who the fewest surviving rivals can still
pick, not just by who's most likely to win. A 13%-champion whose lane is yours
alone can beat a 19%-champion three rivals are also hoarding:
`P(win) × P(solo) > P(win) × P(split)`. Visible history makes this computable.

**Lever 2 — contrarian end-game (the key tactic).** In an **N-player final**
where the other N−1 are forced onto the favourite (`p = P(favourite wins)`):
- pick the favourite → **EV = 1/N** (you split whether it wins, or all bust
  together under the co-elimination rule — that rule is what pins it to 1/N);
- pick the opposition → **EV = 1 − p** (sole winner if they win, else 0).

So **take the opposition whenever `P(opposition) > 1/N`**, i.e. its decimal odds
are **shorter than N**. With N = 5 that's odds < 5.0 (better than 4/1) — almost
always true, since finals are rarely 80%+ one-sided. **The more rivals pile onto
the favourite, the lower the threshold (1/N) and the more aggressively contrarian
you should be.** Same logic applies directionally to any late round.

**Prerequisite — this is why harvesting matters.** To make the contrarian Final
pick you must arrive still *holding* the opposition finalist (unused). Harvesting
shallow teams early means you never burn a finalist, preserving full Final-round
optionality. The early discipline is what *enables* the late EV move — the two
halves lock together.

**Rival model (when built).** Grounded in visible history: constrain each rival
to teams they haven't burned, infer their style from past picks (harvester /
favourite-rider / wildcard), Monte-Carlo the tournament *and* everyone's picks
together, find the furthest-surviving group per world, and average your share to
an EV per candidate strategy.

## Roadmap / TODO
- [ ] **Final-round EV calculator** in `pick.py`: feed the two finalists' odds +
      which rivals can still pick which (from history) → EV of each pick, count of
      rivals stuck on the favourite, and the `1/N` recommendation.
- [ ] **EV mode**: rival-pick model calibrated to visible history; switch from
      survival to expected value once the field is small; flag when EV diverges
      from pure survival.
- [ ] Smarter calibration (proper optimiser; use `match` odds as hard constraints).
- [ ] Quadrant-aware backward-induction policy (the current `planned_assignment`
      over-reserves teams that get eliminated by quadrant rivals).

## Status
Planning / scaffold stage — runs end-to-end on dummy data. Real bracket, odds,
and observed rival picks arrive once the World Cup knockout draw is set; no rush.
