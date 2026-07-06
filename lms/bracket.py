"""The knockout bracket and exact (non-sampled) reach probabilities.

Bracket layout (single elimination, 32 teams):
    slots 0..31 in `teams` order. Matches are consecutive pairs:
    (0,1) (2,3) ... The winner of (0,1) plays the winner of (2,3), etc.
    Quadrant A = slots 0-7, B = 8-15, C = 16-23, D = 24-31.
    One team emerges from each quadrant into the semi-finals.

Rounds and the subtree size a team must "emerge from" to reach the next stage:
    survive R32  -> emerge from a size-2  subtree  (last 16)
    reach  QF    -> emerge from a size-4  subtree  (last 8)
    reach  SF    -> emerge from a size-8  subtree  (last 4)  == market "reach semi"
    reach  Final -> emerge from a size-16 subtree  (last 2)  == market "reach final"
    win          -> emerge from the size-32 subtree          == market "win"
"""

ROUNDS = ["R32", "R16", "QF", "SF", "Final"]

# size of the subtree -> the market marker that size corresponds to
SIZE_TO_MARKER = {8: "reach_semi", 16: "reach_final", 32: "win"}


def make_p(theta):
    """Return p(a beats b) using Bradley-Terry strengths theta[team] > 0."""
    def p(a, b):
        ta, tb = theta[a], theta[b]
        return ta / (ta + tb)
    return p


def emerge_distributions(teams, p, first_round_p=None):
    """Exact probability each team emerges from each power-of-two subtree.

    Returns {size: {team: P(team is the sole survivor of its size-`size` subtree)}}.
    Sanity: sum of size-32 probs == 1, size-16 == 2, size-8 == 4, ...

    `first_round_p` (optional): {team: P(advance)} from the market for the current
    (first) round; when given, the size-2 (first-round) matches use those prices
    instead of the fitted strengths. Lets a half-played round be modelled — decided
    ties forced (p ~ 1/0), pending ties from real odds — consistently with the sim.
    """
    results = {}

    def match_p(a, b, size):
        if size == 2 and first_round_p is not None:
            fa, fb = first_round_p[a], first_round_p[b]
            return fa / (fa + fb)
        return p(a, b)

    def rec(slots):
        if len(slots) == 1:
            return {slots[0]: 1.0}
        mid = len(slots) // 2
        left = rec(slots[:mid])
        right = rec(slots[mid:])
        size = len(slots)
        out = {}
        for t, pt in left.items():
            s = 0.0
            for u, pu in right.items():
                s += pu * match_p(t, u, size)
            out[t] = pt * s
        for u, pu in right.items():
            s = 0.0
            for t, pt in left.items():
                s += pt * match_p(u, t, size)
            out[u] = pu * s
        results.setdefault(size, {}).update(out)
        return out

    rec(list(teams))
    return results


def reach_markers(teams, theta, first_round_p=None):
    """Convenience: {marker: {team: prob}} for whichever markers the current
    bracket size supports. Works at any stage:
        win          = emerge from the whole (size-K) bracket
        reach_final  = emerge from a size-K/2 subtree (last 2)
        reach_semi   = emerge from a size-K/4 subtree (last 4)
    The totals are stage-invariant: 1 champion, 2 finalists, 4 semi-finalists."""
    em = emerge_distributions(teams, make_p(theta), first_round_p)
    k = len(teams)
    out = {"win": em[k]}
    if k // 2 in em:
        out["reach_final"] = em[k // 2]
    if k // 4 in em:
        out["reach_semi"] = em[k // 4]
    return out


ROUND_BY_SIZE = {32: "R32", 16: "R16", 8: "QF", 4: "SF", 2: "Final"}


def round_names_for(n):
    """Round names for an n-team single-elim bracket, largest first.
    e.g. 32 -> [R32,R16,QF,SF,Final]; 16 -> [R16,QF,SF,Final]."""
    names, size = [], n
    while size >= 2:
        names.append(ROUND_BY_SIZE[size])
        size //= 2
    return names


def quadrant_of(slot):
    """Return 'A'/'B'/'C'/'D' for a slot index 0..31."""
    return "ABCD"[slot // 8]


def round_pairs(survivors):
    """Given the list of survivors entering a round (in bracket order),
    return the list of (team_a, team_b) matchups for that round."""
    return [(survivors[i], survivors[i + 1]) for i in range(0, len(survivors), 2)]
