# Last Man Standing — World Cup 2026 strategy explorer

A simulator for a knockout-stage Last-Man-Standing pool. From the **Round of 32**
you pick one team per round; the team must **win** to keep you alive; you may
**never repick** a team. Five rounds: **R32 → R16 → QF → SF → Final**.

> **Live commentary:** [`data/picks.md`](data/picks.md) is the running pick tracker
> + EV analysis for the actual pool as the 2026 knockouts play out.

### Our pool's specifics
- **11 players** entered the knockout (of ~20 who started; qualifying upsets thinned it).
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
python data/sheet_to_json.py   # build engine JSON from the editable data/teams.txt
python pick.py                 # per-stage harvest table + recommended pick
python ev_field.py             # current EV standings for the live pool
python tests/test_odds.py      # sanity tests
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

The live data now holds the **real WC2026 knockout**. `data/teams.txt` is a simple
human-edited sheet (one team per line, in bracket order, with the four prices);
`python data/sheet_to_json.py` converts it to the JSON the engine reads. A
half-played round is handled too — decided ties are locked, pending ties priced,
eliminated teams zeroed.

## How it works
1. **`lms/odds.py`** — decimal odds → vig-free probabilities.
2. **`lms/bracket.py`** — exact reach-probabilities for the bracket (also fills
   in reach-QF / reach-R16, which the markets don't quote). Works at any size.
3. **`lms/calibrate.py`** — fits one Bradley-Terry strength per team so the exact
   reach-probs match the market markers (real match prices folded in as hard
   first-round constraints).
4. **`lms/simulate.py`** — Monte-Carlo: samples whole tournaments.
5. **`lms/strategy.py`** — pick policies + the no-repick / stranded rules.
6. **`lms/ev.py`** — the EV/rival engine: models every player's used-list picking
   to the final under a **save-aware assignment policy** (reserve the champion for
   the final, harvest weak-safe teams early), splits the pot among the furthest
   survivors, and returns each player's expected pot share.
7. **`pick.py`** — per-stage harvest table + recommendation (day-to-day tool).
8. **`ev_field.py`** — current EV standings for the live pool; **`ev_run.py`** —
   compares candidate picks / contrarian plays against the field.
9. **`data/sheet_to_json.py`** — turns the editable `teams.txt` into engine JSON.

## Expected value & opponents (the late-game brain — BUILT, `lms/ev.py`)
Survival vs EV differ because of pot-sharing. The engine below switches on once
the field thins (~QF/SF, down to a handful of players):

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

## Done / roadmap
- [x] Harvest pick helper (`pick.py`) + Monte-Carlo strategy comparison.
- [x] EV/rival engine with pot-sharing (`lms/ev.py`, `ev_field.py`, `ev_run.py`).
- [x] Market match prices folded into calibration (fixes strong-but-trapped teams).
- [x] Half-played-round support (lock decided ties, price pending, zero eliminated).
- [x] Save-aware assignment continuation policy (reserve the champion for the final).
- [ ] Final-round EV calculator surfaced directly in `pick.py`.
- [ ] Auto-ingest the live bracket/odds instead of hand-editing `teams.txt`.

## A neat finding
The within-a-cluster EV order turned out to be **correlation-dependent**: if rivals
all run the identical optimal plan, the player *forced to differ* (because they
burned a key team) wins more *alone*; if rivals diverge realistically, the player
who *kept the strongest hand* wins. Both are true — it's a dial, not a number — and
the tier structure is robust either way. See `data/picks.md` for how it played out.

## Status
Live through the 2026 World Cup knockouts. Engine complete; each round we drop the
surviving teams + fresh odds into `data/teams.txt` and re-run. Running commentary
and standings: [`data/picks.md`](data/picks.md).
