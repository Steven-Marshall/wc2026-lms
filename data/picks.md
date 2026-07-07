# LMS World Cup 2026 — pick tracker & commentary

A Last-Man-Standing pool over the WC2026 knockouts. Each round you pick one team;
it must **win** (advance) or you're out; you can **never repick** a team. The pot
goes to whoever survives longest (split if several tie). 11 players entered the
knockout; picks and history are public. Full method: see the repo README.

---

## 📊 Where we stand — Jul 7 (6 alive, fair share 16.7%)

| # | Player | EV (pot share) | Note |
|--|--|--|--|
| 1 | **Huw** | 18.2% | Through; burned USA (now out — cost him nothing) |
| 2 | **Malley** | 18.0% | Through; burned only weak Belgium — strongest hand |
| 3 | **Matty** | 17.4% | Through; burned Argentina (drifting, so hurts less) |
| 4 | Conrad | 15.8% | Through; burned England (firming — costly) |
| 4 | Andrea | 15.8% | Through; burned England |
| 6 | Hasan | 14.9% | **Pending** — 86% to win his Argentina tie Jul 7 |

**Story so far:** both contrarians (Andy W on Mexico, Mr T on USA) gambled *against*
the crowd and both busted — so the disciplined five who all took **Morocco** are the
front-runners, plus Hasan clinging on. The order among the leaders now re-prices
*daily* with the market: **your standing = the live value of the hand you burned.**
Matty's climbing because Argentina is cooling; Conrad/Andrea are stuck because England
keeps heating up.

---

## Used-team tracker (✗ = eliminated)

| Player | R32 | R16 | QF | SF | Final |
|--|--|--|--|--|--|
| Huw | USA | Morocco | | | |
| Malley | Belgium | Morocco | | | |
| Matty | Argentina | Morocco | | | |
| Conrad | England | Morocco | | | |
| Andrea | England | Morocco | | | |
| Hasan | USA | Argentina *(pending)* | | | |
| Andy W | Argentina | Mexico ✗ | — | — | — |
| Mr T | Egypt | USA ✗ | — | — | — |
| Georgie B | Germany ✗ | — | — | — | — |
| Smarshy (me) | Germany ✗ | — | — | — | — |
| JP | — (no pick) ✗ | — | — | — | — |

**Out (5):** Smarshy & Georgie B (Germany lost R32 on pens), JP (never picked),
Andy W (Mexico, R16), Mr T (USA, R16). **Alive (6):** the five Morocco + Hasan.

---

## Quarter-final bracket
- **Morocco v France** — QF-A
- **Norway v England** — QF-B
- **Spain v Belgium** — QF-C
- **(Argentina/Egypt) v (Switzerland/Colombia)** — QF-D *(R16 ties Jul 7)*

Halves: **France/Morocco + Spain/Belgium** (one finalist) vs **England/Norway +
Argentina's quarter** (the other). So **England's semi wall is Argentina**, and a
**France–Argentina final** is the market's base case.

---

## Results log

**Round of 32 (field 11 → 8).** Out: Smarshy & Georgie B — Germany, an 85% pick and
the model's top harvest, lost to Paraguay on penalties (Germany's first-ever WC
shootout defeat); JP failed to pick. Everyone else through.

**Round of 16 (in progress, 8 → 6):**
- Morocco 3-0 Canada → the five Morocco players **through**.
- England 3-2 Mexico (10 men) → **Andy W out**.
- Belgium 4-1 USA → **Mr T out** (after the Balogun red-card was controversially
  reinstated by FIFA — reportedly following a Trump call to Infantino — USA lost anyway).
- France 1-0 Paraguay, Norway 2-1 Brazil (shock), Spain 1-0 Portugal — no pool picks.
- **Still to play (Jul 7):** Argentina v Egypt (**Hasan**), Switzerland v Colombia.

---

## How the model reads it (for the curious)
- **Harvest early:** spend safe teams that won't go deep anyway (cost you nothing);
  never burn a genuine contender early.
- **Save the champion:** the only team that wins the final *is* the champion, so hold
  your strongest team for last.
- **EV vs survival:** with a small field and a shared pot, being *alone* at the front
  beats being one of a crowd — so late on, calculated contrarianism can pay (the `1/N`
  rule). The engine (`ev_field.py`) simulates every rival's used-list to the final and
  splits the pot to score each player.
