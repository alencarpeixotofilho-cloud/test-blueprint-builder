import math
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from blueprint import alignment, allocate, export, framework  # noqa: E402

FW = ROOT / "examples" / "framework.yaml"


def test_hamilton_sums_to_total():
    for total in [0, 1, 7, 37, 100, 101]:
        out = allocate.hamilton(total, {"a": 0.5, "b": 0.3, "c": 0.2})
        assert sum(out.values()) == total


def test_hamilton_within_one_of_quota():
    w = {"a": 0.33, "b": 0.33, "c": 0.34}
    out = allocate.hamilton(10, w)
    for k, v in out.items():
        assert abs(v - 10 * w[k]) < 1


def test_hamilton_floors():
    out = allocate.hamilton(10, {"a": 0.9, "b": 0.1}, {"b": 4})
    assert out["b"] >= 4 and sum(out.values()) == 10


def test_hamilton_rejects_bad_floors():
    with pytest.raises(ValueError):
        allocate.hamilton(3, {"a": 1, "b": 1}, {"a": 2, "b": 2})


def test_build_totals():
    fw = framework.load(FW)
    bp = allocate.build(fw)
    assert bp["items"].sum() == fw.items
    for n in [40, 60, 120]:
        assert allocate.build(fw, n)["items"].sum() == n


def test_domain_floor_respected():
    fw = framework.load(FW)
    bp = allocate.build(fw, 40)
    assert bp.loc[bp["domain"] == "Internal Medicine", "items"].sum() >= 15


def test_weights_are_normalized():
    fw = framework.load(FW)
    assert math.isclose(sum(fw.domain_weights.values()), 1.0)


def test_invalid_framework():
    with pytest.raises(ValueError):
        framework.from_dict({"items": 0, "domains": {"A": {"weight": 1}}})


def test_alignment_perfect_match():
    fw = framework.load(FW)
    bp = allocate.build(fw)
    exam = bp.loc[bp.index.repeat(bp["items"]), ["domain", "competency", "level"]]
    tab = alignment.compare(bp, exam, "domain")
    assert alignment.alignment_index(tab) == pytest.approx(1.0)
    assert (tab["difference"] == 0).all()


def test_exports(tmp_path):
    fw = framework.load(FW)
    bp = allocate.build(fw)
    md = export.to_markdown(bp, fw.name)
    assert "| **Total** |" in md
    export.to_excel(bp, tmp_path / "b.xlsx")
    tex = export.to_latex(bp, fw.name, tmp_path / "b.tex").read_text(encoding="utf-8")
    assert r"Obstetrics \& Gynecology" in tex
    assert pd.read_excel(tmp_path / "b.xlsx", sheet_name="Cells")["items"].sum() == fw.items


def test_floor_is_a_minimum_not_an_addition():
    out = allocate.hamilton(100, {"a": 0.25, "b": 0.75}, {"a": 15})
    assert out == {"a": 25, "b": 75}
    short = allocate.hamilton(40, {"a": 0.25, "b": 0.75}, {"a": 15})
    assert short == {"a": 15, "b": 25}
