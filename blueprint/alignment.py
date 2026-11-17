"""Check how well a finished exam matches its blueprint."""
from __future__ import annotations

import pandas as pd
from scipy import stats


def compare(bp: pd.DataFrame, exam_items: pd.DataFrame, by: str = "domain") -> pd.DataFrame:
    """Planned vs actual item counts along one dimension (domain, competency, level)."""
    planned = bp.groupby(by)["items"].sum().rename("planned")
    actual = exam_items[by].value_counts().rename("actual")
    t = pd.concat([planned, actual], axis=1).fillna(0).astype(int)
    t["difference"] = t["actual"] - t["planned"]
    t["planned_%"] = 100 * t["planned"] / t["planned"].sum()
    t["actual_%"] = 100 * t["actual"] / max(1, t["actual"].sum())
    return t


def alignment_index(table: pd.DataFrame) -> float:
    """Porter's alignment index: 1 - sum|p_planned - p_actual| / 2 (1 = perfect)."""
    p = table["planned"] / table["planned"].sum()
    a = table["actual"] / max(1, table["actual"].sum())
    return float(1 - (p - a).abs().sum() / 2)


def goodness_of_fit(table: pd.DataFrame) -> dict:
    """Chi-square test of the actual distribution against the planned proportions."""
    t = table[table["planned"] > 0]
    expected = t["planned"] / t["planned"].sum() * t["actual"].sum()
    chi2, p = stats.chisquare(t["actual"], expected)
    return {"chi2": float(chi2), "df": int(len(t) - 1), "p_value": float(p)}


def report(bp: pd.DataFrame, exam_items: pd.DataFrame,
           dimensions=("domain", "competency", "level")) -> dict:
    out = {}
    for dim in dimensions:
        if dim in exam_items.columns:
            tab = compare(bp, exam_items, dim)
            out[dim] = {"table": tab, "alignment_index": alignment_index(tab),
                        **goodness_of_fit(tab)}
    return out
