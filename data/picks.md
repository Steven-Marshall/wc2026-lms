# LMS World Cup 2026 — the complete record

A Last-Man-Standing pool over the WC2026 knockouts. Each round you pick one team;
it must **win** or you're out; you can **never repick**. The game runs until one
player is left standing — and if the tournament runs out of rounds with several
still alive, they are **joint winners**. 11 players entered the knockout.

**🇪🇸 World Champions: Spain.**

---

# 🏆 The result: Huw and Malley split the pot, 50/50

| Player | Finished | Result |
|--|--|--|
| **Huw** | **Joint winner** | **50% of the pot** |
| **Malley** | **Joint winner** | **50% of the pot** |
| Conrad | Final round (France) | — |
| Andrea | Final round (France) | — |
| Matty | Semi-final (England) | — |
| Hasan | Semi-final (England) | — |
| Andy W | Round of 16 (Mexico) | — |
| Mr T | Round of 16 (USA) | — |
| Smarshy | Round of 32 (Germany) | — |
| Georgie B | Round of 32 (Germany) | — |
| JP | Round of 32 (no pick submitted) | — |

The model gave an **84.9% chance this ended in a split.** It split. The single road
to an outright champion needed Argentina to win the final — and Argentina were
dreadful.

---

## The decision that decided everything

Before the last round, Malley faced a choice that looked like *safety versus greed*:

- **France** — the 63.7% favourite in the playoff. Cash something **78.8%** of the
  time. Never win outright.
- **England** — cash only **36.3%** of the time. But the only path to the pot.

He took **England**. And then France — the favourite, the safe one, the one everybody
else was forced onto — **lost 6-4.**

> **Had Malley played France, he would have won nothing at all — and Huw would have
> taken the entire pot as the last man standing.**
>
> The "safe" pick was worth **zero**. The brave pick was worth **half the pot**.
> One man's nerve turned an outright victory into a shared one.

That is the whole tournament in a single decision.

---

## How the last round played out

**3rd/4th playoff: England 6-4 France.** Comfortably the most entertaining match of
the competition. England in a strange formation, Kane on the bench, **4-0 up at half
time** and utterly dominant. Then France scored on 48, 54 and 66 to claw it to 4-3.
Breath-holding until **87'**, when Saka converted a penalty for his second of the
game. France pulled another back in the **6th minute of added time** — 5-4 — before
**Bellingham settled it two minutes later. 6-4.**

**Final: Spain 1-0 Argentina (a.e.t.).** A flat game after that. Spain dominated a
scrappy, negative Argentina — **ten shots on target to none** — and finally broke
through in extra time. Enzo Fernández saw a second yellow. A thoroughly deserved
world title, and a sour note from some of the Argentina players afterwards.

Likely Messi's last World Cup. The one man in blue and white who could hold his head
up at the end, and powerless to change it.

---

## Every prediction, marked

**What the model got right**

- **Huw could never win outright — 0.0%.** Correct. He finished on exactly his
  mathematical ceiling: half the pot.
- **Malley was the only player alive who could win outright.** Correct — the only
  live path to the trophy, and it needed Argentina.
- **Matty, Hasan, Conrad, Andrea: 0.0% to win, from the quarter-finals onward.**
  All four correct. The clone-pair analysis held to the final whistle.
- **84.9% chance of a split.** It split.
- **Huw's quarter-final England pick** — identified at the time as the sharpest move
  of the tournament, worth ~1.7× fair share.

**What it got wrong**

- **The playoff: predicted France 3-1. It finished England 6-4.** Wrong winner,
  wrong by six goals. The *fixture* read was right — "expect a goal-fest, England
  will concede" — the result was not.
- **The anti-Argentina prior.** The model *penalised* Argentina on the assumption a
  largely English field would shun them. Four of six picked them. The bias hadn't
  vanished — it had **inverted**, because Argentina were now England's opponent.
- **Early on, the model claimed holding both France and Spain was pointless**
  ("they'd kill each other in the semi"). Huw proved otherwise and built his whole
  quarter-final around it.

**And the caveat that earned its keep.** Every round, this document warned that the
third-place playoff was the least trustworthy number on the board — the most
motivation-distorted fixture in football, and unmodellable. A 63.7% favourite lost
**6-4** in a game nobody wanted to play, and it decided the pool.

---

## Full results log

**Round of 32 (11 → 8).** Germany, an 85% pick and the model's top harvest, lost to
Paraguay on penalties — **Smarshy and Georgie B out**. **JP never submitted a pick**.

**Round of 16 (8 → 6).** Morocco 3-0 Canada. England 3-2 Mexico with ten men →
**Andy W out**. Belgium 4-1 USA → **Mr T out**. Argentina 3-2 Egypt from two goals
down → **Hasan survives**. Switzerland beat Colombia on penalties. France 1-0
Paraguay, Norway 2-1 Brazil, Spain 1-0 Portugal.

**Quarter-finals (6 → 6, everybody through).** France 2-0 Morocco. Spain beat
Belgium. **England 2-1 Norway (a.e.t.)** — Huw's contrarian gamble comes off.
Argentina beat Switzerland.

**Semi-finals (6 → 4).** **Spain 2-0 France** — the favourite falls, but nobody's
pick was in that game. **Argentina 2-1 England**, England leading 1-0 after half time
before sitting on it and being caught in added time → **Matty and Hasan out**.

**Final round (4 → 2).** **England 6-4 France** in the playoff → **Conrad and Andrea
out**, Malley through. **Spain 1-0 Argentina (a.e.t.)** in the final → Huw through.
No rounds remaining. **Huw and Malley declared joint winners.**

---

## Final used-team tracker

| Player | R32 | R16 | QF | SF | Final round |
|--|--|--|--|--|--|
| **Huw** | USA | Morocco | England | Argentina | **Spain ✅** |
| **Malley** | Belgium | Morocco | Spain | Argentina | **England ✅** |
| Conrad | England | Morocco | Spain | Argentina | France ✗ |
| Andrea | England | Morocco | Spain | Argentina | France ✗ |
| Matty | Argentina | Morocco | Spain | England ✗ | — |
| Hasan | USA | Argentina | Spain | England ✗ | — |
| Andy W | Argentina | Mexico ✗ | — | — | — |
| Mr T | Egypt | USA ✗ | — | — | — |
| Georgie B | Germany ✗ | — | — | — | — |
| Smarshy | Germany ✗ | — | — | — | — |
| JP | *(no pick)* ✗ | — | — | — | — |

---

**A full post-mortem — what we learned about strategy, herds, hedging and rule
design — is in [`RETROSPECTIVE.md`](../RETROSPECTIVE.md).**

*Model: Bradley-Terry strengths fitted to vig-free market odds; exact bracket
probabilities; Monte-Carlo through the middle rounds; the endgame solved exactly as
a game, every world enumerated, best-response iteration to equilibrium.*
