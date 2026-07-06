"""Pick policies and the evaluation harness.

A *policy* decides which team to pick each round, given only information that
would be available at decision time (who is alive now, the strengths/markets) --
never the realised future of the simulation. The harness then reveals whether
that pick won its match in that particular simulated tournament.

Core rules enforced by the harness:
  * a pick must be a team playing this round that has not been used before;
  * surviving the round requires that team to win its match;
  * if no legal (alive + unused) team exists, you are STRANDED -- your run ends
    there. This is the "reach the final with no team to pick" case: it can only
    pay out if every other survivor also goes out in the same round (modelled
    later, once opponents are added).
"""
from .bracket import ROUNDS, make_p
from .simulate import participants, winner_of_match_containing


class Context:
    def __init__(self, teams, theta, market, markers):
        self.teams = teams          # bracket order
        self.theta = theta          # fitted strengths
        self.market = market        # vig-free market markers
        self.markers = markers      # model reach-probs {marker: {team: p}}
        self._p = make_p(theta)

    def opponent(self, sim, rnd, team):
        for a, b, _ in sim[rnd]:
            if team == a:
                return b
            if team == b:
                return a
        return None

    def p_win_match(self, sim, rnd, team):
        opp = self.opponent(sim, rnd, team)
        return self._p(team, opp) if opp is not None else 0.0


# ----- policies: (rnd, sim, used, legal, ctx) -> chosen team -------------------

def greedy_safe(rnd, sim, used, legal, ctx):
    """Each round, pick the legal team most likely to win its match THIS round.
    Ignores the future entirely -- the baseline that tends to 'waste' teams it
    needed later."""
    return max(legal, key=lambda t: ctx.p_win_match(sim, rnd, t))


def save_favourite(rnd, sim, used, legal, ctx):
    """Earmark the outright favourite as the Final pick; never spend them earlier
    unless they are the only legal option. Otherwise greedy-safe."""
    champion = _argmax(ctx.market["win"])
    if rnd == "Final":
        return champion if champion in legal else greedy_safe(rnd, sim, used, legal, ctx)
    others = [t for t in legal if t != champion]
    pool = others if others else legal  # forced to spend champion only if nothing else
    return max(pool, key=lambda t: ctx.p_win_match(sim, rnd, t))


def planned_assignment(rnd, sim, used, legal, ctx):
    """Backward-induction flavour: reserve the deepest-running teams for the
    latest rounds (champion -> Final, runner-up -> SF, a semi-finalist -> QF),
    and harvest safe-but-shallow wins early. Falls back to greedy if a reserved
    team is already out."""
    champion = _argmax(ctx.market["win"])
    runner_up = _argmax(ctx.market["reach_final"], exclude={champion})
    qf_pick = _argmax(ctx.market["reach_semi"], exclude={champion, runner_up})
    reserved = {"Final": champion, "SF": runner_up, "QF": qf_pick}

    target = reserved.get(rnd)
    if target is not None and target in legal:
        return target

    # early rounds (or fallback): safest legal team that isn't a reserved future pick
    reserved_future = {reserved[r] for r in ROUNDS[ROUNDS.index(rnd) + 1:] if r in reserved}
    pool = [t for t in legal if t not in reserved_future] or legal
    return max(pool, key=lambda t: ctx.p_win_match(sim, rnd, t))


POLICIES = {
    "greedy_safe": greedy_safe,
    "save_favourite": save_favourite,
    "planned_assignment": planned_assignment,
}


# ----- harness ----------------------------------------------------------------

def run_policy_on_sim(policy, sim, ctx):
    used = set()
    survived = 0
    stranded = None
    picks = []
    for rnd in ROUNDS:
        legal = [t for t in participants(sim, rnd) if t not in used]
        if not legal:
            stranded = rnd
            break
        pick = policy(rnd, sim, used, legal, ctx)
        if pick not in legal:  # defensive: never let a policy cheat the rules
            pick = max(legal, key=lambda t: ctx.p_win_match(sim, rnd, t))
        used.add(pick)
        picks.append((rnd, pick))
        if winner_of_match_containing(sim, rnd, pick) == pick:
            survived += 1
        else:
            break
    return {"survived": survived, "full": survived == len(ROUNDS),
            "stranded": stranded, "picks": picks}


def _argmax(prob_by_team, exclude=()):
    exclude = set(exclude)
    best, best_p = None, -1.0
    for t, p in prob_by_team.items():
        if t in exclude:
            continue
        if p > best_p:
            best, best_p = t, p
    return best
