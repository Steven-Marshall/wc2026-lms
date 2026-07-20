# What I learned building a model for a Last Man Standing pool

*World Cup 2026. Eleven friends, one pot, five knockout rounds — and a fortnight
spent discovering that the interesting problem wasn't the football.*

---

## The game

From the Round of 32 you pick one team per round. It must win — extra time and
penalties count. **You can never pick the same team twice.** Last player standing
takes the pot; if the tournament runs out of rounds with several still alive, they
split it.

That's it. It sounds like a football quiz. It is actually a constrained optimisation
problem wrapped in a simultaneous-move game against people who know exactly what
you've already spent.

I built a model: Bradley-Terry team strengths fitted to vig-free betting odds, exact
bracket probabilities, Monte-Carlo through the middle rounds, and — once the field
thinned — an exact game-theoretic solver that enumerated every remaining world.

Here's what it taught us. The football lessons came first; the human ones turned out
to matter more.

---

## Part 1: The strategy

### Harvest early, and never burn a contender

Because you can't repick, every pick has two costs: the risk it loses, and the
*option value* you destroy by spending it. The right early pick is a heavy favourite
that was never going deep anyway — a strong side stuck in a brutal quadrant, safe
this week and irrelevant later. Spending it costs nothing.

**Score = P(win this match) × (1 − how much you'll want them later).**

### Save the champion

Only one team wins the final, so the only way to win outright is to arrive holding
the eventual champion. Work backwards: Final = champion, semi = runner-up, and
everything earlier is filler. Every early pick is really a decision about what you're
*protecting*.

### Asymmetric elimination

Your standing moves on matches you have no stake in. A team you already burned
getting knocked out **helps** you — your spend cost nothing, and rivals lose a weapon
they still held. A team you burned going deep **hurts** you. We re-ran the board after
every result, including games nobody had picked, and the leaderboard shuffled every
time.

### The pot is won in the semis, not the final

The most counter-intuitive result. Splitting each strategy's value into "won in the
semis" versus "won at the final" showed the **final contributes a flat ~10% to every
strategy** — a commodity. All the separation between a good plan and a great one came
from *how often your pick left you the last one standing before the final was even
played.* For the sharpest lines, two-thirds of the value was won a round early.

We had all been planning routes to a final that mostly didn't decide anything.

---

## Part 2: The crowd

### Contrarian value decays brutally with company

With a shared pot, being *right* isn't enough — you have to be right **alone**. We
priced the same contrarian lane at different levels of crowding:

| Players in the lane | Value |
|--|--|
| 1 | 27% (with a 20% chance of the whole pot) |
| 2 | ~20% (solo chance collapses to ~0) |
| 6 | ~17% — i.e. nothing, just fair share |

**The edge is in the lane, not the player.** Swapping *who* stood in a lane barely
moved the numbers; changing *how many* stood there moved everything.

### A unanimous field is un-killable

Our platform's rules contained a line nobody had read: *if every active player picks
a loser in a round, nobody goes out.*

So if all six survivors pick the same team and it loses — **nothing happens.** The
herd is immortal. Which produces the tournament's best strategic insight:

> **The lone defector doesn't dodge the herd's risk. He arms it.**

When five players took Spain and one took England, that one pick converted the
group's shared risk from *harmless* into *lethal* — because now it was no longer true
that everyone had picked a loser. He had a 17% chance of ending the entire
competition on the spot. He didn't sidestep their correlation; he weaponised it.

### Clone pairs: when you mathematically cannot win

Two players who have burned identical teams have identical options — so they make
identical picks, survive and die together in every possible world, and **can never
separate.** To win outright you need your pick to win *and* every other survivor's to
lose. Against your own clone, that second condition isn't unlikely, it's impossible.

By the quarter-finals, four of the six survivors sat in two such pairs. All four were
mathematically eliminated from *winning* while still very much alive in the
competition. Two of them went on to top the EV table — leading a race they could not
finish.

### The volunteer's dilemma

Those pairs could escape — one of them had only to make a deliberately suboptimal
pick to break the symmetry. But the payoff matrix was vicious:

- Jumping was **strictly dominated** — whatever your twin did, you were better off
  staying.
- The jump was **a gift to your twin**: the volunteer got a 4% shot; the one who
  stayed put was freed of his clone and landed the best hand on the board.
- And if both jumped, they were clones again — back to zero, and poorer.

Collectively they'd have been richer if exactly one moved. Individually, nobody
should. They were *rationally* trapped at zero. Only unenforceable collusion could
have saved them, and picks were simultaneous.

---

## Part 3: The humans (where the model was worst)

### Everyone was playing a different game

The model optimised **expected share of the pot**. Watching the picks come in, it
became obvious the players were optimising **P(I'm among the winners)** — *"I just
want to win something, even if it's a big split."*

Those are different objectives and they recommend different picks. At one point the
model's advice for the same player flipped completely depending on which you chose:
maximise EV and he plays one team; maximise "cash anything" and he abandons his whole
strategy to join the herd — for a 44% chance of a share and a **0%** chance of
winning.

A shared pot quietly changes what game people are playing. If ties split, "don't get
knocked out" feels right, everyone herds onto the safest team — **and the safest team
guarantees a share while foreclosing a win.** A field of survival-maximisers
optimises its way into a stalemate.

**Design lesson: if you want a Last Man Standing pool to actually produce one, don't
split ties — roll the pot over.** The moment a split stops counting as a win, the
herding incentive dies.

### Psychological hedging is real — and the model had the sign backwards

My biggest miss. The field was mostly English, so I put a **penalty** on Argentina in
the opponent model — nobody would pick them, for reasons.

Then England drew Argentina in the semi-final and **four of six picked Argentina.**

The bias hadn't disappeared. It had **inverted** — because Argentina were now the team
standing in England's way. "Anti-Argentina" never meant *"I won't pick Argentina."* It
meant *"I want England to win."* And once Argentina were England's opponent, backing
them became **insurance against your own heartbreak**:

- England win → you're out of the pool, but your team's in the World Cup Final.
- Argentina win → you're gutted, but you've advanced and you're getting paid.

**You cannot have a bad night.** They weren't maximising money. They were minimising
regret.

> **The behavioural prior belongs on the outcome a player *wants*, not on a team —
> and its effect on their pick flips sign depending on who's on the other side of the
> fixture.** Model fans, not gamblers.

And it has a corollary I liked a lot. The only two who *refused* to hedge — England on
the pitch and England in the pool — ended up with **double the field's expected
value.** They were being paid a premium for carrying the risk everyone else laid off.
A pool of football fans is an insurance market, and the un-hedged are the
underwriters. (Both were knocked out that same night. That's what underwriting is.)

---

## Part 4: Never change the rules mid-tournament

Two-thirds of the way through, the platform proposed merging the third-place playoff
into the final round — so the last round would have **four** teams playing (both
finalists plus both beaten semi-finalists) instead of two.

It sounds administrative. We modelled it. It was a demolition:

1. **It deleted stranding.** With four teams playing you can essentially never be
   locked out — and stranding was the game's only real constraint. It's why saving
   your champion mattered. Remove the punishment and every strategic idea becomes
   decoration.
2. **It doubled the number of winning teams.** Two right answers instead of one,
   roughly halving the chance anyone is left standing alone. It created a category
   that cannot exist under the old rules: two players both "correct" — one backing the
   World Cup winner, one backing the third-place winner — carving up the pot.
3. **It handed the casting vote to the least predictable match in football.** By the
   end, **more of the pool's outcomes were decided by the third-place playoff than by
   the World Cup Final.**

Net effect: an **89.6%** chance that "Last Man Standing" ended with nobody standing
alone.

And the politics were visible in the numbers. The player pushing hardest for the
change was, by the model's arithmetic, its single biggest beneficiary; the player who
stood to lose most was the one who'd played the best hand. Picks were already locked,
so it was a retroactive repricing. **If a rule needs fixing, fix it before the next
tournament.**

---

## Part 5: How it ended

Two matches left. One player, Malley, faced a choice that looked like safety versus
greed:

- **France** — a 63.7% favourite. Cash something 78.8% of the time. Never win.
- **England** — cash only 36.3% of the time. The only path to the pot.

He took England. France lost the playoff **6-4**, in comfortably the best match of the
tournament — 4-0 at half time, back to 4-3 by the 66th minute, a penalty on 87, and
two more in added time.

> **Had he played it safe, he'd have won nothing — and his rival would have taken the
> entire pot as the last man standing.**
>
> The safe pick was worth zero. The brave pick was worth half the pot.

Spain beat Argentina 1-0 in the final, so the other survivor came through too. **Two
joint winners, 50/50** — exactly the split the model had said was 85% likely.

---

## What the model got right, and wrong

**Right:** every "this player can no longer win outright" call — four of them, made
at the quarter-finals and correct to the final whistle. The overwhelming likelihood
of a split. The best pick of the tournament, identified in real time. The whole
harvest/save-the-champion framework.

**Wrong:** the behavioural prior, with the sign inverted. An early bracket error
(corrected by a human who knew his draw better than I did). A claim that holding both
same-half favourites was pointless — which one player promptly disproved and built his
quarter-final around. And a confident **France 3-1** prediction for a game that
finished **England 6-4**.

**The most useful thing it produced** wasn't a pick. It was a warning it repeated
every single round: *the third-place playoff is the least trustworthy number here —
tired legs, no glory, nobody wants to be there, and no model can price it.*

That match finished 6-4, knocked out a 63.7% favourite, and decided the pot.

**The model was at its best describing structure — who can still win, who's trapped,
where the value hides. It was at its worst predicting people and dead rubbers.** Which
is, on reflection, exactly the right way round.
