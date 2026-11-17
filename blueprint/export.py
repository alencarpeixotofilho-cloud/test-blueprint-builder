"""Export a blueprint to Markdown, Excel and LaTeX."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .allocate import summary

TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "blueprint.tex"


def to_markdown(bp: pd.DataFrame, title: str = "Test blueprint") -> str:
    s = summary(bp)
    lines = [f"# {title}", "", "## Domain × cognitive level", ""]
    cols = ["Domain", *s.columns]
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "---|" * len(cols))
    for idx, row in s.iterrows():
        cells = [f"**{idx}**" if idx == "Total" else str(idx)] + [str(int(v)) for v in row]
        lines.append("| " + " | ".join(cells) + " |")
    lines += ["", "## Detailed cells", "", "| Domain | Competency | Level | Items |", "|---|---|---|---:|"]
    for r in bp.itertuples():
        if r.items:
            lines.append(f"| {r.domain} | {r.competency} | {r.level} | {r.items} |")
    return "\n".join(lines) + "\n"


def to_excel(bp: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        summary(bp).to_excel(xw, sheet_name="Summary")
        bp.to_excel(xw, sheet_name="Cells", index=False)
        bp.groupby(["domain", "competency"])["items"].sum().unstack(fill_value=0) \
          .to_excel(xw, sheet_name="Domain x competency")
    return path


def _tex_escape(s: str) -> str:
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#")]:
        s = s.replace(a, b)
    return s


def to_latex(bp: pd.DataFrame, title: str, path: str | Path) -> Path:
    s = summary(bp)
    ncols = len(s.columns)
    head = " & ".join(["\\textbf{Domain}", *[f"\\textbf{{{_tex_escape(c)}}}" for c in s.columns]]) + r" \\"
    body = []
    for idx, row in s.iterrows():
        cells = [_tex_escape(str(idx)), *[str(int(v)) for v in row]]
        if idx == "Total":
            body.append(r"\midrule")
            cells = [f"\\textbf{{{c}}}" for c in cells]
        body.append(" & ".join(cells) + r" \\")
    detail = []
    for dom, g in bp[bp["items"] > 0].groupby("domain", sort=False):
        detail.append(f"\\multicolumn{{3}}{{l}}{{\\textbf{{{_tex_escape(dom)}}}}} \\\\")
        for r in g.itertuples():
            detail.append(f"\\quad {_tex_escape(r.competency)} & {_tex_escape(r.level)} & {r.items} \\\\")
    tex = TEMPLATE.read_text(encoding="utf-8")
    tex = (tex.replace("<<TITLE>>", _tex_escape(title))
              .replace("<<COLSPEC>>", "l" + "r" * ncols)
              .replace("<<HEAD>>", head)
              .replace("<<BODY>>", "\n".join(body))
              .replace("<<DETAIL>>", "\n".join(detail))
              .replace("<<TOTAL>>", str(int(bp["items"].sum()))))
    path = Path(path)
    path.write_text(tex, encoding="utf-8")
    return path
