"""Tiny JSONC loader: standard JSON plus `//` line comments and trailing commas.

Lets the data files (bracket.jsonc, markets.jsonc) be hand-annotated while you
type in real odds, without pulling in a YAML dependency.
"""
import json
import re


def loads(text):
    # strip // line comments (not inside strings) -- good enough for our data files
    out_lines = []
    for line in text.splitlines():
        in_str = False
        esc = False
        cut = None
        for i, ch in enumerate(line):
            if esc:
                esc = False
                continue
            if ch == "\\":
                esc = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if ch == "/" and not in_str and i + 1 < len(line) and line[i + 1] == "/":
                cut = i
                break
        out_lines.append(line if cut is None else line[:cut])
    cleaned = "\n".join(out_lines)
    # remove trailing commas before } or ]
    cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
    return json.loads(cleaned)


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return loads(f.read())
