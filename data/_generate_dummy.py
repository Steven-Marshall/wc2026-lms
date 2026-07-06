"""Generate internally-consistent DUMMY data so the pipeline runs before the
real Round-of-32 is known.

We invent hidden team strengths, compute the EXACT reach-probabilities from the
bracket, then turn those into decimal betting odds with a realistic bookmaker
margin (overround) and a bid/ask spread -- i.e. exactly the shape of data you'll
type in for real. Because the odds come from known strengths, calibration should
roughly recover them, which is a built-in sanity check.

Run:  python data/_generate_dummy.py
Overwrites data/bracket.jsonc and data/markets.jsonc.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lms.bracket import emerge_distributions, make_p, round_pairs  # noqa: E402

# 32 teams in bracket order; quadrant A=0-7, B=8-15, C=16-23, D=24-31.
# strength is a hidden Bradley-Terry rating (bigger = stronger). DUMMY values.
TEAMS = [
    # Quadrant A (slots 0-7): England is the lone heavyweight
    ("England", 6.5), ("Senegal", 2.0), ("Mexico", 2.2), ("Qatar", 0.8),
    ("Netherlands", 2.4), ("Ecuador", 1.4), ("USA", 2.0), ("Wales", 1.3),
    # Quadrant B (slots 8-15): Brazil clear
    ("Brazil", 7.5), ("Switzerland", 1.9), ("Uruguay", 2.3), ("Ghana", 1.2),
    ("Portugal", 2.6), ("Iran", 1.0), ("Japan", 1.8), ("Canada", 1.5),
    # Quadrant C (slots 16-23): France AND Spain -- they must knock each other out
    ("France", 6.8), ("Poland", 1.5), ("Denmark", 2.2), ("Saudi Arabia", 0.7),
    ("Spain", 6.0), ("Cameroon", 1.1), ("Croatia", 2.4), ("Serbia", 1.7),
    # Quadrant D (slots 24-31): Argentina AND Germany -- same problem
    ("Argentina", 7.2), ("Australia", 1.3), ("Belgium", 2.8), ("Tunisia", 0.9),
    ("Germany", 6.2), ("Costa Rica", 0.9), ("Colombia", 2.2), ("Korea", 1.6),
]

WIN_MARGIN = 1.25       # ~25% overround on the 32-runner outright market
FINAL_MARGIN = 1.14
SEMI_MARGIN = 1.09
MATCH_MARGIN = 1.05
SPREAD = 0.012          # bid/ask half-width


def price(prob, margin):
    shown = min(prob * margin, 0.999)
    return 1.0 / shown


def quote(prob, margin, as_pair=True):
    """Return a decimal price, as [bid, ask] or a single number."""
    center = price(prob, margin)
    if not as_pair:
        return round(center, 2)
    return [round(center * (1 - SPREAD), 2), round(center * (1 + SPREAD), 2)]


def main():
    names = [n for n, _ in TEAMS]
    theta = {n: s for n, s in TEAMS}
    em = emerge_distributions(names, make_p(theta))
    win, final, semi = em[32], em[16], em[8]

    # current round (R32) match odds, normalised pairwise from true strengths
    pairs = round_pairs(names)
    p = make_p(theta)

    def jdump_map(d, margin, fmt="{:.2f}"):
        lines = []
        for i, n in enumerate(names):
            as_pair = (i % 4 != 0)  # mix single + [bid,ask] to exercise both
            q = quote(d[n], margin, as_pair=as_pair)
            val = "[{}, {}]".format(*q) if isinstance(q, list) else fmt.format(q)
            comma = "," if i < len(names) - 1 else ""
            lines.append(f'    "{n}": {val}{comma}')
        return "\n".join(lines)

    match_block_lines = []
    flat_idx = 0
    for a, b in pairs:
        pa = p(a, b)
        for nm, pr in ((a, pa), (b, 1 - pa)):
            q = quote(pr, MATCH_MARGIN, as_pair=(flat_idx % 3 != 0))
            val = "[{}, {}]".format(*q) if isinstance(q, list) else "{:.2f}".format(q)
            comma = "," if flat_idx < len(names) - 1 else ""
            match_block_lines.append(f'    "{nm}": {val}{comma}')
            flat_idx += 1
    match_block = "\n".join(match_block_lines)

    here = os.path.dirname(os.path.abspath(__file__))

    bracket_txt = (
        "// DUMMY bracket -- 32 teams in slot order. Matches are consecutive pairs.\n"
        "// Quadrant A = slots 0-7, B = 8-15, C = 16-23, D = 24-31; one team from\n"
        "// each quadrant reaches the semi-finals. Replace teams once the real\n"
        "// Round of 32 is set (keep them in bracket order!).\n"
        "{\n"
        '  "format": "single-elimination, 32 teams, 4 quadrants",\n'
        '  "rounds": ["R32", "R16", "QF", "SF", "Final"],\n'
        '  "teams": [\n'
        + ",\n".join(f'    "{n}"' for n in names)
        + "\n  ]\n}\n"
    )

    markets_txt = (
        "// DUMMY market odds -- decimal prices for a $1 stake.\n"
        "// A single number is a firm price; [bid, ask] is a back/lay spread (we take the mid).\n"
        "// These need NOT sum to 100%: overround is removed by normalising each market\n"
        "// to its known total (win->1, reach_final->2, reach_semi->4, each match->1).\n"
        "{\n"
        '  "current_round": "R32",\n\n'
        '  // to win the tournament\n'
        '  "win": {\n' + jdump_map(win, WIN_MARGIN) + "\n  },\n\n"
        '  // to reach the final (last 2)\n'
        '  "reach_final": {\n' + jdump_map(final, FINAL_MARGIN) + "\n  },\n\n"
        '  // to reach the semi-finals (last 4)\n'
        '  "reach_semi": {\n' + jdump_map(semi, SEMI_MARGIN) + "\n  },\n\n"
        '  // current-round match odds (one entry per team playing this round)\n'
        '  "match": {\n' + match_block + "\n  }\n}\n"
    )

    with open(os.path.join(here, "bracket.jsonc"), "w", encoding="utf-8") as f:
        f.write(bracket_txt)
    with open(os.path.join(here, "markets.jsonc"), "w", encoding="utf-8") as f:
        f.write(markets_txt)
    print("wrote data/bracket.jsonc and data/markets.jsonc")
    print(f"hidden top strengths: Brazil/Argentina/France favourites; "
          f"true champion prob (Brazil)={win['Brazil']:.3f}")


if __name__ == "__main__":
    main()
