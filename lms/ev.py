"""Expected-value engine: model the whole field of players (each with their own
used-list) picking through the remaining rounds, then split the pot among the
furthest survivors — so we can score a focal pick by EV, not just survival.

Rival model: each round a rival picks from its legal (alive + unused) teams by a
softmax over the harvest score  P(win this match) x (1 - opportunity cost).
  * temp = 0  -> deterministic best harvest (the sharp "everyone piles on the
                 same team" case).
  * temp > 0  -> progressively more spread / noisier field.
Opportunity cost is stage-aware: reach-semi while >=16 teams remain, then
reach-final at the QF, then win-the-cup from the semis (the champion is the save).

Pot rules: the pot is split equally among whoever survives the most rounds
(covers both multiple outright winners and same-round co-elimination).
"""
import math
import random

from .bracket import round_names_for
from .simulate import participants, winner_of_match_containing


def _opp_marker(teams_in_round):
    if teams_in_round >= 16:
        return "reach_semi"
    if teams_in_round == 8:
        return "reach_final"
    return "win"


def _harvest(ctx, sim, rnd, team, m):
    # At the final (2 teams) there is no future round, so opportunity cost is
    # nil -- you simply want the team that wins it (this is where a saved
    # champion gets cashed in).
    if m <= 2:
        return ctx.p_win_match(sim, rnd, team)
    opp = ctx.markers[_opp_marker(m)].get(team, 0.0)
    return ctx.p_win_match(sim, rnd, team) * (1.0 - opp)


def _choose(ctx, sim, rnd, legal, m, rng, temp):
    scored = [(t, _harvest(ctx, sim, rnd, t, m)) for t in legal]
    if temp <= 0:
        return max(scored, key=lambda x: x[1])[0]
    ws = [math.exp(s / temp) for _, s in scored]
    tot = sum(ws)
    r = rng.random() * tot
    acc = 0.0
    for (t, _), w in zip(scored, ws):
        acc += w
        if r <= acc:
            return t
    return scored[-1][0]


def run_field(ctx, sim, rivals, focal, rng, temp=0.0):
    """Play every player through the bracket for one simulated tournament.
    `rivals`: list of {name, used:[...]}. `focal`: {used:[...], r16_pick: team|None}.
    Returns {name: rounds_survived} including key '_focal'."""
    rounds = round_names_for(len(ctx.teams))
    state = {p["name"]: {"used": set(p["used"]), "alive": True, "n": 0} for p in rivals}
    state["_focal"] = {"used": set(focal.get("used", [])), "alive": True, "n": 0}

    for ri, rnd in enumerate(rounds):
        parts = participants(sim, rnd)
        m = len(parts)
        for name, st in state.items():
            if not st["alive"]:
                continue
            legal = [t for t in parts if t not in st["used"]]
            if not legal:
                st["alive"] = False          # stranded: no legal pick
                continue
            if name == "_focal" and ri == 0 and focal.get("r16_pick"):
                pick = focal["r16_pick"] if focal["r16_pick"] in legal \
                    else _choose(ctx, sim, rnd, legal, m, rng, 0.0)
            elif name == "_focal":
                pick = _choose(ctx, sim, rnd, legal, m, rng, 0.0)   # focal = sharp after R16
            else:
                pick = _choose(ctx, sim, rnd, legal, m, rng, temp)  # rivals
            st["used"].add(pick)
            if winner_of_match_containing(sim, rnd, pick) == pick:
                st["n"] += 1
            else:
                st["alive"] = False
    return {name: st["n"] for name, st in state.items()}


def run_field_fixed(ctx, sim, players, rng, temp=0.0):
    """Like run_field but every player has a fixed R16 pick (their actual choice),
    then plays greedy from the QF on. `temp` adds decision-noise to those
    continuation picks so otherwise-identical players (e.g. a herd) diverge
    realistically instead of clustering and splitting forever. players: [{name,
    used, r16}]."""
    rounds = round_names_for(len(ctx.teams))
    state = {p["name"]: {"used": set(p["used"]), "alive": True, "n": 0, "r16": p.get("r16")}
             for p in players}
    for ri, rnd in enumerate(rounds):
        parts = participants(sim, rnd)
        m = len(parts)
        for st in state.values():
            if not st["alive"]:
                continue
            legal = [t for t in parts if t not in st["used"]]
            if not legal:
                st["alive"] = False
                continue
            if ri == 0 and st["r16"] and st["r16"] in legal:
                pick = st["r16"]
            else:
                pick = _choose(ctx, sim, rnd, legal, m, rng, temp)
            st["used"].add(pick)
            if winner_of_match_containing(sim, rnd, pick) == pick:
                st["n"] += 1
            else:
                st["alive"] = False
    return {name: st["n"] for name, st in state.items()}


def evaluate_field(ctx, sims, players, pot=1.0, seed=7, temp=0.0):
    """Per-player EV / survival for a field of actual R16 picks."""
    rng = random.Random(seed)
    agg = {p["name"]: {"ev": 0.0, "r16": 0, "solo": 0, "money": 0} for p in players}
    for sim in sims:
        res = run_field_fixed(ctx, sim, players, rng, temp)
        best = max(res.values())
        winners = [nm for nm, k in res.items() if k == best]
        for nm, k in res.items():
            if k >= 1:
                agg[nm]["r16"] += 1
            if k == best:
                agg[nm]["ev"] += pot / len(winners)
                agg[nm]["money"] += 1
                if len(winners) == 1:
                    agg[nm]["solo"] += 1
    n = len(sims)
    return [{"name": p["name"], "r16": p.get("r16"),
             "p_survive_r16": agg[p["name"]]["r16"] / n, "ev": agg[p["name"]]["ev"] / n,
             "p_solo_win": agg[p["name"]]["solo"] / n,
             "p_in_money": agg[p["name"]]["money"] / n} for p in players]


def evaluate_pick(ctx, sims, rivals, focal_used, r16_pick, temp=0.0, pot=1.0, seed=1):
    """EV (and outcome breakdown) for the focal player taking `r16_pick` at R16,
    then playing sharp, against `rivals`, over the given simulated tournaments."""
    rng = random.Random(seed)
    n_rounds = len(round_names_for(len(ctx.teams)))
    total = solo = shared = out_alone = reached_end = 0.0
    for sim in sims:
        res = run_field(ctx, sim, rivals, {"used": focal_used, "r16_pick": r16_pick},
                        rng, temp)
        best = max(res.values())
        winners = [nm for nm, k in res.items() if k == best]
        f = res["_focal"]
        if f == best:
            total += pot / len(winners)
            if len(winners) == 1:
                solo += 1
            else:
                shared += 1
        # focal knocked out while at least one rival survives strictly further
        if f < best:
            out_alone += 1
        if f == n_rounds:
            reached_end += 1
    n = len(sims)
    return {"pick": r16_pick or "sharp", "ev": total / n, "p_solo": solo / n,
            "p_shared": shared / n, "p_out_behind": out_alone / n,
            "p_win_all": reached_end / n}
