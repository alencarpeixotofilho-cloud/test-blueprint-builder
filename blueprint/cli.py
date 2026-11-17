"""Command-line interface.

    python -m blueprint build --framework examples/framework.yaml --out out/
    python -m blueprint check --framework examples/framework.yaml --exam examples/exam_items.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from . import alignment, allocate, export, framework


def cmd_build(a):
    fw = framework.load(a.framework)
    bp = allocate.build(fw, a.items)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    bp.to_csv(out / "blueprint.csv", index=False)
    (out / "blueprint.md").write_text(export.to_markdown(bp, fw.name), encoding="utf-8")
    export.to_excel(bp, out / "blueprint.xlsx")
    export.to_latex(bp, fw.name, out / "blueprint.tex")
    print(allocate.summary(bp).to_string())
    print(f"\nWritten: blueprint.csv, .md, .xlsx, .tex in {out}")


def cmd_check(a):
    fw = framework.load(a.framework)
    bp = allocate.build(fw)
    exam = pd.read_csv(a.exam)
    res = alignment.report(bp, exam)
    for dim, r in res.items():
        print(f"\n== {dim} ==  alignment index = {r['alignment_index']:.3f}   "
              f"chi2({r['df']}) = {r['chi2']:.2f}, p = {r['p_value']:.3f}")
        print(r["table"].round(1).to_string())


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build and check test blueprints.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="allocate items and export the blueprint")
    b.add_argument("--framework", required=True)
    b.add_argument("--items", type=int, default=None, help="override the item count")
    b.add_argument("--out", default="out")
    b.set_defaults(func=cmd_build)
    c = sub.add_parser("check", help="compare a finished exam with the blueprint")
    c.add_argument("--framework", required=True)
    c.add_argument("--exam", required=True, help="CSV with domain, competency, level per item")
    c.set_defaults(func=cmd_check)
    a = ap.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
