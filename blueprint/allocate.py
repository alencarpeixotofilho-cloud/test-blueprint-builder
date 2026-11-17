"""Integer allocation of items to blueprint cells.

Proportional targets are rarely whole numbers (25% of 37 items = 9.25). We use
the **largest-remainder (Hamilton) method** hierarchically:

1. domains get their share of the total (respecting optional floors);
2. inside each domain, items are split across competencies;
3. inside each (domain, competency) cell, items are split across cognitive levels.

Every step preserves the parent total exactly, so the final table always sums
to the requested number of items, and no cell deviates from its exact
proportional target by one item or more at its own level.
"""
from __future__ import annotations

import math

import pandas as pd

from .framework import Framework


def hamilton(total: int, weights: dict[str, float], floors: dict[str, int] | None = None) -> dict[str, int]:
    """Largest-remainder apportionment of ``total`` units by ``weights``.

    Optional ``floors`` are *minimums*: a key whose proportional share falls
    below its floor is fixed at the floor and the remaining units are
    re-apportioned among the other keys (repeated until stable).
    """
    if total < 0:
        raise ValueError("total must be non-negative")
    floors = {k: int((floors or {}).get(k, 0)) for k in weights}
    if sum(floors.values()) > total:
        raise ValueError("floors exceed total")
    if sum(weights.values()) <= 0:
        raise ValueError("weights must sum to a positive number")

    fixed: dict[str, int] = {}
    while True:
        free = {k: w for k, w in weights.items() if k not in fixed}
        remaining = total - sum(fixed.values())
        wsum = sum(free.values())
        quotas = {k: remaining * w / wsum if wsum > 0 else 0.0 for k, w in free.items()}
        below = [k for k, q in quotas.items() if q < floors[k]]
        if not below:
            break
        for k in below:
            fixed[k] = floors[k]

    alloc = {k: math.floor(q) for k, q in quotas.items()}
    left = remaining - sum(alloc.values())
    # ties broken by larger weight, then by name for determinism
    order = sorted(quotas, key=lambda k: (-(quotas[k] - alloc[k]), -weights[k], k))
    for k in order[:left]:
        alloc[k] += 1
    alloc.update(fixed)
    return {k: alloc[k] for k in weights}


def build(fw: Framework, items: int | None = None) -> pd.DataFrame:
    """Full blueprint as a long table: domain, competency, level, items, target."""
    n = items or fw.items
    dom_alloc = hamilton(n, fw.domain_weights, {d.name: d.min_items for d in fw.domains})
    rows = []
    for d in fw.domains:
        comp_alloc = hamilton(dom_alloc[d.name], d.competencies)
        for comp, k in comp_alloc.items():
            lvl_alloc = hamilton(k, fw.cognitive_levels)
            for lvl, m in lvl_alloc.items():
                target = n * d.weight * d.competencies[comp] * fw.cognitive_levels[lvl]
                rows.append({"domain": d.name, "competency": comp, "level": lvl,
                             "items": m, "target": round(target, 2)})
    return pd.DataFrame(rows)


def summary(bp: pd.DataFrame) -> pd.DataFrame:
    """Domain x cognitive level cross-table with totals (the classic 2-way blueprint)."""
    t = bp.pivot_table(index="domain", columns="level", values="items", aggfunc="sum", fill_value=0)
    t = t[[c for c in bp["level"].unique()]]
    t["Total"] = t.sum(axis=1)
    t.loc["Total"] = t.sum(axis=0)
    return t
