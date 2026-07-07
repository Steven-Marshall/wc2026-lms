# LMS WC2026 — Knockout pick tracker

11 players entered the knockout. No repicks allowed (used-list grows each round).
JP failed to pick in R32 → effectively out (only survives if the entire field
busts the round, which won't happen).

## Used-team tracker  (✗ = eliminated)
| Player | R32 | R16 | QF | SF | Final |
|--|--|--|--|--|--|
| Andy W | Argentina | Mexico ✗ | — | — | — |
| Hasan | USA | Argentina | | | |
| Mr T | Egypt | USA ✗ | — | — | — |
| Georgie B | Germany ✗ | — | — | — | — |
| Conrad | England | Morocco | | | |
| Huw | USA | Morocco | | | |
| Andrea | England | Morocco | | | |
| Malley | Belgium | Morocco | | | |
| **Smarshy (me)** | **Germany ✗** | — | — | — | — |
| Matty | Argentina | Morocco | | | |
| JP | — (no pick) ✗ | — | — | — | — |

## R16 picks + EV read (engine on the real field, market-accurate)
Field: Morocco ×5 (Matty, Huw, Conrad, Andrea, Malley), Argentina ×1 (Hasan),
USA ×1 (Mr T), Mexico ×1 (Andy W). Fair share = 12.5%.
## R16 results (live)
- **Morocco 3-0 Canada** (Jul 4) → **Matty, Huw, Conrad, Andrea, Malley THROUGH to QF.**
- **England 3-2 Mexico** (10 men) → **Andy W ELIMINATED** (his Mexico coin-flip missed). England to QF.
- **Norway 2-1 Brazil** (shock) → Brazil OUT (no pool pick; symmetric loss). QF-B = Norway v England.
- **Belgium 4-1 USA** (Jul 6) → **Mr T ELIMINATED** (2nd contrarian gone; Balogun's
  red card was controversially reinstated by FIFA — reportedly after Trump rang
  Infantino — and USA lost 4-1 anyway). **Spain 1-0 Portugal** → Spain through, Ronaldo out.
- QF now: Morocco v France | Norway v England | Spain v Belgium | (Arg/Egy)–(Swi/Col).
- Still to play: Argentina–Egypt (Hasan, Jul 7), Switzerland–Colombia.
- Field: 6 alive = 5 Morocco (through) + Hasan (pending). Out: Smarshy, Georgie B, JP, Andy W, Mr T.

## Standings (Jul 7, fresh odds, 6 alive, fair share 16.7%)
Huw 18.2 · Malley 18.0 (best hands, neck-and-neck) > **Matty 17.4** (up — Argentina
drifted to 3rd fav so his burn hurts less) > Conrad/Andrea 15.8 (England firming keeps
their burn costly) > Hasan 14.9 (86% to win his Argentina tie tomorrow). Leaderboard now
re-prices daily with the market: your standing = the live value of the hand you burned.
Contrarians both dead (Andy W/Mexico, Mr T/USA). Calibration clean (~1pp).
- Field: OUT (4) = Smarshy, Georgie B, JP, Andy W. ALIVE (7) = 5 Morocco (through) + Hasan, Mr T (pending).
- Morocco holding = the "Moro WIN" EV branch: herd now best-positioned (~15% each, Malley
  leads on his stronger kept hand); Hasan halved to ~11.7% (mid); breakaways Mr T ~7% / Andy W
  ~6.5% at the bottom, still needing to win their coin-flip ties.

CURRENT standings — R16 half-played (Morocco/France/Norway/England through; Spain/USA/
Argentina/Colombia ties pending). Engine: save-aware assignment continuation policy,
market R16 prices locked, moderate rival plan-divergence. 7 alive, fair share 14.3%.
| Player | R16 pick | Spent early | Survive R16 | EV |
|--|--|--|--|--|
| **Malley** | Morocco | Belgium | 99.9% | **17.4%** (best hand) |
| Huw | Morocco | USA | 99.9% | 17.2% |
| Matty | Morocco | Argentina | 99.9% | 15.6% |
| Conrad/Andrea | Morocco | England | 99.9% | 14.1% (worst of herd) |
| Hasan | Argentina (pending) | USA | 84.9% | 13.1% |
| Mr T | USA (pending) | Egypt | 52.9% | 8.5% |
Key insights: (1) Morocco holding neutralised the contrarians — Hasan from pre-round
hero to mid-pack, Mr T clinging to a coin-flip. (2) Within the safe herd, EV = QUALITY OF
HAND KEPT: Malley/Huw (spent weak Belgium/USA) lead; Conrad/Andrea (burned England, now a
red-hot 3rd favourite) are WORST — England's rise made that the costliest burn. (3) The
within-herd order is genuinely correlation-dependent: pure-optimal rivals reward the forced
differentiator (Matty), realistic divergence rewards the best hand (Malley) — tier structure
robust either way. Model = save-aware assignment policy (lms/ev.py, feature branch).

## R32 results (live)
Completed (12 of 16). Pool picks in **bold**:
- **England 2-1 DR Congo** — Conrad + Andrea THROUGH (Kane winner, squeaky).
- **USA 2-0 Bosnia** — Hasan + Huw THROUGH (comfortable).
- **Belgium 3-2 Senegal** — Malley THROUGH (survived the coin-flip).
- **Germany OUT** (1-1 Paraguay, lost 3-4 pens) → Smarshy + Georgie B ELIMINATED.
- Non-pool: France 3-0 Sweden, Spain 3-0 Austria, Portugal 2-1 Croatia,
  Mexico 2-0 Ecuador, Norway 2-1 Ivory Coast, Brazil 2-1 Japan, Canada 1-0 SA,
  Morocco bt Netherlands (pens), Paraguay bt Germany (pens).
- R16 bracket CONFIRMED (matches our build): A: Canada-Morocco, Paraguay-France |
  B: Brazil-Norway, Mexico-England | C: Portugal-Spain, USA-Belgium |
  D: Arg/CV-Aus/Egy, Swi/Alg-Col/Gha. France gets Paraguay in R16 — path is a stroll.

R32 COMPLETE. July 3: Argentina 3-2 Cape Verde (AET, scare) → Andy W + Matty through;
**Egypt beat Australia on pens → Mr T THROUGH** (corrected — the 57% coin-flip held on spot-kicks);
Colombia 1-0 Ghana, Switzerland 2-0 Algeria (both through).

FINAL R32 FIELD: 11 -> 8. OUT (3) = Smarshy, Georgie B (Germany), JP (no pick).
THROUGH (8) = Andy W, Matty (Argentina), Hasan, Huw (USA), Conrad, Andrea (England), Malley (Belgium), Mr T (Egypt).

## R16 bracket (locked) — each survivor picks a NEW team (can't repick their R32 team)
A: Canada v Morocco | Paraguay v France
B: Brazil v Norway | Mexico v England
C: Portugal v Spain | USA v Belgium
D: Argentina v Egypt | Switzerland v Colombia
Harvest options: Morocco (v Canada, ~72% qualify — crowd pick) and Colombia (v Switzerland
— differentiation, both feed a giant [France/Argentina] in QF so disposable). All 8 survivors free to take either.

Bracket notes:
- France cruised 3-0 Sweden; quadrant (Germany+NL out) is a stroll — clear favourite.
- Quadrant C sub-plot: USA (Hasan/Huw) meet Belgium (Malley) in the R16 — but both
  teams are already "used", so it doesn't affect their next picks (just a curiosity).

Note: pick process was sound — Germany was an 85% advance / optimal harvest. The 15% tail hit on penalties. Right call, wrong coin-flip.

## R32 tally
- **Germany ×2** — Georgie B, me
- **USA ×2** — Hasan, Huw
- **Argentina ×2** — Andy W, Matty
- **England ×2** — Conrad, Andrea
- **Egypt ×1** — Mr T
- **Belgium ×1** — Malley
- **No pick** — JP

## Grading the field — two axes
Did you (1) avoid burning a contender [low reach-semi], and (2) keep the match safe [high win prob]?

|  | Safe match (✓) | Risky match (✗) |
|--|--|--|
| **Disposable team (✓)** | **Germany 85%/15%, USA 83%/15%** — optimal | **Egypt 57%, Belgium 62%** — right idea, reckless match |
| **Burned a contender (✗)** | **Argentina 92%/60%, England 86%/36%** — safe tonight, torched the long game | (nobody — small mercy) |

### Reads
- **Sharp (got it): Georgie B, me (Germany); Hasan, Huw (USA).** Safe win, nothing wasted.
- **Greedy-safe trap: Andy W, Matty (Argentina); Conrad, Andrea (England).** Safest matches on the board, but they spent contenders. Argentina is the worst offence — it's the easiest path to the final (60% reach-semi); those two can **never ride Argentina again**, which is the single most valuable lane to hold. England a lesser version of the same mistake.
- **Gamblers: Mr T (Egypt 57%), Malley (Belgium 62%).** Didn't burn a contender (good), but took coin-flip matches into round 1 — the live bust risks tonight.
- **Out: JP** (no pick).

### Tonight's likely thinning
8 players are 80%+ favourites and should sail through. The casualties come from the
tail: **Mr T (Egypt, 43% bust), Malley (Belgium, 38% bust), JP (gone).** Expect the
field to drop from 11 to roughly 8–9.

### My position
On Germany — safe, fully disposable, **every contender still in my pocket**
(Argentina, France, Spain, England, Brazil…). 4 rivals have already burned a
contender. Among the sharpest quartile of the field.
