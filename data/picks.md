# LMS World Cup 2026 — pick tracker & commentary

A Last-Man-Standing pool over the WC2026 knockouts. Each round you pick one team;
it must **win** (advance) or you're out; you can **never repick** a team. The pot
goes to whoever survives longest (split if several tie). 11 players entered the
knockout; picks and history are public. Full method: see the repo README.

---

## 🐙 The one-line answer for the quarters

> **Pick Spain.** It's the obvious, safe pick. **But France is a lovely contrarian
> — and honestly, *every* one of the sensible plays is playable.** That's not a
> cop-out; it falls out of the maths. Read on.

Six of us are left, all through to the quarters, and here's the thing that makes
this round fun: **we're all holding almost the same hand,** so the "obvious" pick
is a shared pick — and shared picks are worth less than they look.

---

## Where we stand — quarter-finals (6 alive, fair share 16.7%)

Everyone left burned **Morocco** in the last 16 and is now looking at the same
board. Because we're so bunched, the plain-vanilla standings are nearly flat
(everyone ~16–18%). The interesting question isn't *who's ahead* — it's *what to
pick next*, because that's where people will separate.

**The quarter-final bracket**

| Quarter | Match | Half |
|--|--|--|
| A | **Morocco v France** | 1 |
| C | **Spain v Belgium** | 1 |
| B | **Norway v England** | 2 |
| D | **Argentina v Switzerland** | 2 |

The key bit of geography: **France and Spain are in the *same half*** — they'd meet
in the semi, so **only one of them can reach the final.** England and Argentina are
the other half, and that semi is a coin-flip.

Model's read (vig-stripped): **France 33%** to win the cup, **Spain 19%**,
**Argentina 19%**, **England 17%**. To even win the quarter: France 79%, Spain 75%,
Argentina 73%, England 66%.

---

## The four plays

Since France and Spain share a half, one of them is a "disposable" for you — you
can only carry one of them past the semi. Everything comes down to **which finalist
you choose to hold.** Four sensible routes (QF pick / SF pick / Final pick):

| # | Play | Nickname | The idea |
|--|--|--|--|
| 1 | **Spain → England → France** | *the safe one* | Burn Spain now, hold France for the final. What most people will do. |
| 2 | **Spain → France → England** | *the patriotic one* | Burn Spain, ride France through the semi, hold **England** for the final. |
| 3 | **Spain → Argentina → France** | *"I burned England"* | For those who can't use England — ride Argentina through the semi instead. |
| 4 | **France → (semi) → Spain** | *"I'm hoping you all pick Spain!"* | Burn **France** now (it's the safer QF win anyway), and keep **Spain** as your champion. |

All four are live. **The catch with play 1** is that it's what *everyone* does — so
if France goes on to win the cup (the single most likely outcome), the whole pack
holding France just **splits the pot.** Being one of six on the same ticket caps
your upside hard.

**Play 4 (keep Spain)** is the sharp mischief. Burning France in the quarter costs
you nothing (France is actually the *safer* win this round), and holding Spain only
pays off in the exact worlds where Spain beats France in the semi — which is
precisely when everyone *else's* France ticket is torn up. You win big and often
alone. The more people pile onto France, the better this gets.

---

## The twist: **the pot is usually won in the semis, not the final**

Here's the counter-intuitive bit that reframes everything. We instinctively plan a
full route *to the final* — but the pot goes to whoever lasts longest, and that's
often decided a round **early**: if your semi pick leaves you the last one standing,
you've already won, and it doesn't matter that you "used up" a team for a final you
never have to play.

When you split each play's expected value into *"won in the semis"* vs *"won at the
final"*, two things pop out:

- **The "won at the final" slice is a flat ~10% for every single play.** The final
  is a commodity — every route cashes about the same there.
- **So *all* the difference between a good play and a great one is in the
  *semis*** — i.e. *how often your pick makes you the last one standing before the
  final even kicks off.* For the sharpest plays, **two-thirds of the value is
  won in the semi round.**

And the cheeky consequence: the team almost nobody wants to pick — **Argentina** —
is the best *semi vehicle* on the board. While the field crowds onto England in
that half, Argentina winning its semi (it's a coin-flip) **knocks the whole England
crowd out in one result** — and leaves whoever rode Argentina standing alone. The
squeamish pick is the strong one.

**Bottom line:** Spain is fine and safe. France (keeping Spain) is the value play.
The plays that route through Argentina quietly win the most *in the semis*. There
is no wrong sensible answer here — only more or less crowded ones. **Being alone is
the whole game.**

---

## Used-team tracker (✗ = eliminated)

| Player | R32 | R16 | QF | SF | Final |
|--|--|--|--|--|--|
| Huw | USA | Morocco | | | |
| Malley | Belgium | Morocco | | | |
| Matty | Argentina | Morocco | | | |
| Conrad | England | Morocco | | | |
| Andrea | England | Morocco | | | |
| Hasan | USA | Argentina | | | |
| Andy W | Argentina | Mexico ✗ | — | — | — |
| Mr T | Egypt | USA ✗ | — | — | — |
| Georgie B | Germany ✗ | — | — | — | — |
| Smarshy (me) | Germany ✗ | — | — | — | — |
| JP | — (no pick) ✗ | — | — | — | — |

**Out (5):** Smarshy & Georgie B (Germany, R32 pens), JP (never picked), Andy W
(Mexico, R16), Mr T (USA, R16). **Alive (6):** the five Morocco players + Hasan.

Two quiet constraints worth noting: **Conrad and Andrea burned England**, so they
*can't* hold it — which nudges them toward that Argentina semi vehicle. And nobody
has burned France or Spain, so the "keep Spain" play is open to everyone.

---

## Results log

**Round of 32 (11 → 8).** Out: Smarshy & Georgie B — Germany, an 85% pick and the
model's top harvest, lost to Paraguay on penalties (Germany's first-ever WC shootout
defeat); JP failed to pick. Everyone else through.

**Round of 16 (8 → 6).** Complete.
- Morocco 3-0 Canada → the five Morocco players **through**.
- England 3-2 Mexico (10 men) → **Andy W out**.
- Belgium 4-1 USA → **Mr T out**.
- **Argentina 3-2 Egypt** — from 2-0 down! → **Hasan survives**.
- Switzerland beat Colombia on penalties (0-0).
- France 1-0 Paraguay, Norway 2-1 Brazil (shock), Spain 1-0 Portugal — no pool picks.

**Quarter-finals:** to play. Six alive, all Morocco + Hasan, picking from the board
above.

---

## How the model reads it (for the curious)
- **Harvest early:** spend safe teams that won't go deep anyway; never burn a
  genuine contender early.
- **Save the champion:** the only team that wins the final *is* the champion, so
  hold your strongest team for last — unless you're being a contrarian on purpose.
- **Alone > in a crowd:** with a shared pot, being the *sole* survivor is worth far
  more than being one of a pack — so the value is in picking the finalist (or semi
  vehicle) the crowd *isn't* on. The engine (`ev_field.py`, `ev_deviation.py`,
  `ev_where_won.py`) simulates every rival's used-list to the final, splits the pot,
  and scores each play — including *which round* the pot gets won.
