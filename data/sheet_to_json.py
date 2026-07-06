"""Convert the human-edited data/teams.txt into the tool's JSON inputs.

    python data/sheet_to_json.py

Reads data/teams.txt (32 lines in bracket/slot order, pipe-separated:
pos | team | win_tie | reach_semi | reach_final | win_cup). When all 32 slots
have a team and all four odds, writes data/bracket.jsonc and data/markets.jsonc.
Otherwise it just reports progress (and writes nothing), so you can fill the
sheet in over several sittings as the draw firms up.

Odds cells accept a single price (7.5) or a bid/ask (7.4/7.6 -> [7.4, 7.6]).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "teams.txt")


def parse_odds(cell):
    cell = cell.strip()
    if not cell:
        return None
    if "/" in cell:
        a, b = cell.split("/", 1)
        return [float(a), float(b)]
    return float(cell)


def read_sheet(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.split("#", 1)[0].strip()  # drop comments
            if not line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 6:
                continue
            pos, team = parts[0], parts[1]
            odds = [parse_odds(parts[i]) for i in range(2, 6)]
            rows.append({"pos": pos, "team": team, "odds": odds})
    return rows


def odds_literal(v):
    if isinstance(v, list):
        return "[{}, {}]".format(*v)
    return repr(v)


def write_json(rows):
    teams = [r["team"] for r in rows]
    win_tie = {r["team"]: r["odds"][0] for r in rows}
    semi = {r["team"]: r["odds"][1] for r in rows}
    final = {r["team"]: r["odds"][2] for r in rows}
    win = {r["team"]: r["odds"][3] for r in rows}

    def block(d):
        return ",\n".join(f'    "{t}": {odds_literal(d[t])}' for t in teams)

    bracket_txt = (
        "// Generated from data/teams.txt — do not edit by hand.\n"
        "{\n"
        '  "format": "single-elimination, 32 teams, 4 quadrants",\n'
        '  "rounds": ["R32", "R16", "QF", "SF", "Final"],\n'
        '  "teams": [\n'
        + ",\n".join(f'    "{t}"' for t in teams)
        + "\n  ]\n}\n"
    )
    markets_txt = (
        "// Generated from data/teams.txt — do not edit by hand.\n"
        "{\n"
        '  "current_round": "R32",\n\n'
        '  "win": {\n' + block(win) + "\n  },\n\n"
        '  "reach_final": {\n' + block(final) + "\n  },\n\n"
        '  "reach_semi": {\n' + block(semi) + "\n  },\n\n"
        '  "match": {\n' + block(win_tie) + "\n  }\n}\n"
    )
    with open(os.path.join(HERE, "bracket.jsonc"), "w", encoding="utf-8") as f:
        f.write(bracket_txt)
    with open(os.path.join(HERE, "markets.jsonc"), "w", encoding="utf-8") as f:
        f.write(markets_txt)


def main():
    rows = read_sheet(SHEET)
    named = [r for r in rows if r["team"] and r["team"].upper() != "TBD"]
    complete = [r for r in named if all(o is not None for o in r["odds"])]

    n = len(rows)
    is_pow2 = n >= 2 and (n & (n - 1)) == 0
    print(f"Sheet: {n} slots | {len(named)} named | "
          f"{len(complete)} fully priced  (need all {n} priced to build)")

    if not is_pow2:
        print(f"  ! slot count must be a power of two (2..32), found {n} — check teams.txt")
    pending_team = [r["pos"] for r in rows if not r["team"] or r["team"].upper() == "TBD"]
    if pending_team:
        print(f"  teams still TBD ({len(pending_team)}): {', '.join(pending_team)}")
    missing_odds = [r["team"] for r in named if any(o is None for o in r["odds"])]
    if missing_odds:
        print(f"  named but unpriced ({len(missing_odds)}): {', '.join(missing_odds)}")

    if is_pow2 and len(complete) == n:
        write_json(rows)
        print("  -> wrote data/bracket.jsonc and data/markets.jsonc. Ready: python run.py / pick.py")
    else:
        print("  -> not complete yet; JSON not written (existing files untouched).")


if __name__ == "__main__":
    main()
