# LMS World Cup 2026 — pick tracker & commentary

A Last-Man-Standing pool over the WC2026 knockouts. Each round you pick one team;
it must **win** or you're out; you can **never repick**. The game runs until one
player is left standing. If the tournament runs out of rounds with several still
alive, they are **joint winners**. And — crucially — *if every active player picks
a loser in a round, nobody goes out.* 11 players entered the knockout.

---

## 🐙 Two rounds left. And four of you cannot win.

That is not a figure of speech. **Matty, Hasan, Conrad and Andrea have a 0.0%
chance of winning this competition outright.** Not "small" — zero. They are
mathematically locked into sharing the pot. Read on; it's the best thing the model
has found all tournament.

---

## Where we are

**Semi-finals:** France v Spain · England v Argentina
**Final round:** the **Final** *and* the **3rd/4th playoff** are played together —
so **all four teams are playing**, and you may pick any of them. You survive the
round if your pick wins **its own match**.

That last rule matters enormously: **nobody can be stranded any more.** Whatever
you don't spend in the semi is guaranteed to be playing somewhere.

**The market (vig-free):** France **59.2%** to beat Spain · England **55.9%** to
beat Argentina (England is now favourite — it was a coin-flip before the quarters).
Outrights: France 39.1%, England 22.1%, Spain 21.1%, Argentina 17.8%.

**Who holds what**

| Player | Burned (of the four) | Still holds |
|--|--|--|
| **Huw** | England | **France, Spain, Argentina** |
| **Malley** | Spain | **France, England, Argentina** |
| Matty | Spain, Argentina | France, England |
| Hasan | Spain, Argentina | France, England |
| Conrad | Spain, England | France, Argentina |
| Andrea | Spain, England | France, Argentina |

---

## The board (exact — no simulation, every world enumerated)

| Player | Semi | Final round | EV | **Chance of winning outright** |
|--|--|--|--|--|
| **Huw** | France | Spain *(in the playoff)* | **18.5%** | 10.4% |
| Conrad | Argentina | France | 17.5% | **0.0%** |
| Andrea | Argentina | France | 17.5% | **0.0%** |
| **Malley** | England | Argentina | 16.8% | **13.3%** |
| Matty | England | France | 14.8% | **0.0%** |
| Hasan | England | France | 14.8% | **0.0%** |

**How it ends:** solo winner **23.7%** · 2-way split **41.2%** · 3-way split **35.2%**.

Note the inversion at the top: **Huw has the better EV, but Malley has the better
chance of actually winning.** Huw's hand is worth more; Malley's is worth *winning*.

---

## Why four of you can't win

**1. Playing France in the final round is a guaranteed split.** The model puts it at
exactly **0.0%** — anyone who plays France cannot win outright. Here's the trap:

- France **wins** its match → everyone on France survives → joint winners → **split**.
- France **loses** → they *all* picked a loser → the all-lose rule fires → everyone
  continues → but there are no rounds left → joint winners → **split**.

Same outcome either way. France is the safest team on the board — it wins its
final-round match ~62% *whether it's in the Final or the playoff* — and that safety
is precisely the cage. **It buys you a guaranteed share and forecloses a win.**

**2. You are travelling in identical pairs.** This is the killer.

> **Matty and Hasan hold exactly the same two teams.** So do **Conrad and Andrea.**

Identical constraints force identical picks. Which means each twin **survives and
dies with the other, in every single world.** Even when their France wins, their
clone's France also wins. They can never separate, so they can never stand alone.
They are not playing for the pot — they are playing to *share it with the one person
they can never shake off.*

To win outright you need two things: your pick to win, **and every other survivor's
pick to lose.** Against your own clone, that second condition is not unlikely — it
is *impossible*. It isn't misfortune. It's arithmetic.

---

## The way out — and why nobody will take it

There *is* an escape. Any of the four can manufacture a shot at winning by spending
**France in the semi** and keeping their other team for the final round. It's a
"suboptimal" pick that buys a real chance.

Except the moment you write down the actual game, it turns into something far
crueller. Here is each pair's 2×2 — **payoffs shown for the row player:**

**Matty vs Hasan**

| | Hasan **stays** | Hasan **jumps** |
|--|--|--|
| **Matty stays** | EV 14.8%, win **0%** | **EV 25.9%, win 15.0%** |
| **Matty jumps** | EV 12.6%, win 4.3% | EV 7.9%, win **0%** |

**Conrad vs Andrea**

| | Andrea **stays** | Andrea **jumps** |
|--|--|--|
| **Conrad stays** | EV 17.5%, win **0%** | **EV 30.7%, win 26.2%** |
| **Conrad jumps** | EV 12.0%, win 4.3% | EV 13.4%, win **0%** |

Three things fall out, and they get progressively worse:

**1. Jumping is a *dominated* move.** Whatever your twin does, you are better off
staying. Andrea jumps? Conrad should stay (30.7 beats 13.4). Andrea stays? Conrad
should stay (17.5 beats 12.0). **Staying wins in every column.** So a rational
Conrad never jumps — nor does Andrea — and they both collect their guaranteed **0%**.

**2. The jump is a gift to your twin, not to yourself.** If Andrea jumps, *she* gets
a meagre 4.3% and her EV *falls* to 12.0 — while **Conrad, who did nothing at all,
is freed of his clone and rockets to EV 30.7% with a 26.2% chance of winning
outright.** That is the best hand on the entire board — better than Huw's. **The
escape hatch only opens for the person who didn't jump.**

**3. And if you both jump, you're clones again** — straight back to 0%, and Matty and
Hasan end up *poorer* than if they'd both stayed (7.9% vs 14.8%).

So this isn't a game of chicken. **It's a volunteer's dilemma.** Each pair would be
collectively richer if exactly one of them jumped (Conrad + Andrea: 42.7% of the pot
between them, versus 35.0% if both sit tight) — but **the volunteer personally pays
for it, and hands the windfall to the very man he's trying to beat.**

Nobody volunteers. They are *rationally* trapped at zero.

**The only true escape is collusion.** If Conrad and Andrea could agree — *"you jump,
I stay, and we split whatever I win"* — that is jointly +7.7 points of EV and turns a
0% into a 26.2% shot at the pot. Perfectly rational. Entirely unenforceable. And the
picks are simultaneous.

Which leaves us here: **four men, in two pairs, each quietly praying his twin loses
his nerve first.** Game theory says neither will.

---

## Huw, again

Huw's optimal line is to **spend France in the semi.** Burning his best team looks
like heresy. It's the same move that won him the quarter-finals.

France is his **safest semi gate** (59.2%), and spending it leaves him holding
**Spain and Argentina** — the weapons to play *against* a France-laden field in the
final round. He then plays **Spain in the third-place playoff.** In the world where
France loses the Final while Spain wins the playoff, **the pot is his alone.**

Which is worth sitting with for a second: **the model's best line for the tournament
leader is to ignore the World Cup Final entirely and back a team in the dead
rubber.** Under the old rules that route did not exist.

Malley runs the same idea one notch weaker (defect with Argentina) — which is exactly
why he's clear of Matty and Hasan despite an identical semi pick, and why he has the
best chance of anyone of actually lifting the thing.

---

## Used-team tracker (✗ = eliminated)

| Player | R32 | R16 | QF | SF | Final |
|--|--|--|--|--|--|
| Huw | USA | Morocco | England | | |
| Malley | Belgium | Morocco | Spain | | |
| Matty | Argentina | Morocco | Spain | | |
| Hasan | USA | Argentina | Spain | | |
| Conrad | England | Morocco | Spain | | |
| Andrea | England | Morocco | Spain | | |
| Andy W | Argentina | Mexico ✗ | — | — | — |
| Mr T | Egypt | USA ✗ | — | — | — |
| Georgie B | Germany ✗ | — | — | — | — |
| Smarshy (me) | Germany ✗ | — | — | — | — |
| JP | — (no pick) ✗ | — | — | — | — |

---

## Results log

**R32 (11 → 8).** Germany lost to Paraguay on penalties — an 85% pick, and the
model's top harvest. Smarshy and Georgie B out; JP never picked.

**R16 (8 → 6).** Morocco 3-0 Canada. England 3-2 Mexico → **Andy W out**.
Belgium 4-1 USA → **Mr T out**. Argentina 3-2 Egypt from 2-0 down → **Hasan
survives**. Switzerland beat Colombia on pens.

**Quarter-finals (6 → 6 — everyone through).**
- **France 2-0 Morocco.**
- **Spain beat Belgium** → the five Spain-pickers survive.
- **England 2-1 Norway (a.e.t., 1-1 at 90)** → **Huw survives.**
- **Argentina beat Switzerland.**

Huw's England gamble came off. Had Belgium won, he would have been the last man
standing and the game would already be over — he was a one-in-six shot from ending
it in the quarters.

---

## The honest caveat

Huw's optimal line — and a big slice of everyone's EV — now runs **through the
third-place playoff**, and the model prices that game on pure team strength. In
reality a 3rd/4th playoff is the most motivation-distorted fixture in football:
tired legs, no glory, nobody wants to be there. **The model cannot see any of that.**

So treat every playoff-dependent number here as the least trustworthy on the board.
The pool leader's best strategy now depends on the single most unmodellable match of
the tournament. That is a direct consequence of merging the playoff into the final
round — make of it what you will.

---

## How the model works
Bradley-Terry team strengths fitted to the vig-free market (match odds + outrights),
then the endgame is solved **exactly** — all 16 worlds enumerated, no Monte Carlo —
as a game, with best-response iteration to a Nash equilibrium. See `endgame.py`,
`endgame_solve.py`, `endgame_outcomes.py`.
