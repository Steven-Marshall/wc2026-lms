"""Run policies over the Monte-Carlo sims and summarise the survival distribution.

For v1 (just modelling me, single fixed pot) the headline numbers are:
  * P(survive each round)
  * P(full 5/5)  -- an outright win subject to the share rules
  * P(stranded)  -- reached a round with no legal pick (final-with-no-team risk)
  * mean rounds survived
Expected-value / pot-sharing comes once opponents are added.
"""
from .bracket import ROUNDS
from .strategy import POLICIES, run_policy_on_sim


def evaluate(policy_name, sims, ctx):
    policy = POLICIES[policy_name]
    n = len(sims)
    survive_at_least = {r: 0 for r in ROUNDS}
    full = 0
    stranded = 0
    rounds_sum = 0
    for sim in sims:
        res = run_policy_on_sim(policy, sim, ctx)
        rounds_sum += res["survived"]
        for i in range(res["survived"]):
            survive_at_least[ROUNDS[i]] += 1
        if res["full"]:
            full += 1
        if res["stranded"] is not None:
            stranded += 1
    return {
        "policy": policy_name,
        "p_survive": {r: survive_at_least[r] / n for r in ROUNDS},
        "p_full": full / n,
        "p_stranded": stranded / n,
        "mean_rounds": rounds_sum / n,
    }


def format_table(results):
    cols = ["policy"] + [f"thru {r}" for r in ROUNDS] + ["5/5", "stranded", "mean"]
    rows = [cols]
    for r in results:
        row = [r["policy"]]
        row += [f"{r['p_survive'][rd] * 100:5.1f}%" for rd in ROUNDS]
        row += [f"{r['p_full'] * 100:5.2f}%", f"{r['p_stranded'] * 100:5.1f}%",
                f"{r['mean_rounds']:.2f}"]
        rows.append(row)
    widths = [max(len(str(row[i])) for row in rows) for i in range(len(cols))]
    out = []
    for ri, row in enumerate(rows):
        out.append("  ".join(str(c).rjust(widths[i]) for i, c in enumerate(row)))
        if ri == 0:
            out.append("  ".join("-" * widths[i] for i in range(len(cols))))
    return "\n".join(out)
