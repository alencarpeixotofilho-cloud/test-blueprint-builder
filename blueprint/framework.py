"""Reference-framework definition and validation.

A framework is a YAML file describing *what* an exam should measure and in
which proportions::

    name: Sample clinical-sciences framework
    items: 100
    domains:
      Internal Medicine:
        weight: 0.25
        min_items: 10            # optional floor
        competencies:            # optional; weights within the domain
          Diagnosis: 0.4
          Management: 0.4
          Prevention: 0.2
    cognitive_levels:            # applied inside every domain
      Recall: 0.2
      Application: 0.5
      Analysis: 0.3
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Domain:
    name: str
    weight: float
    min_items: int = 0
    competencies: dict[str, float] = field(default_factory=dict)


@dataclass
class Framework:
    name: str
    items: int
    domains: list[Domain]
    cognitive_levels: dict[str, float]

    @property
    def domain_weights(self) -> dict[str, float]:
        return {d.name: d.weight for d in self.domains}


def _normalize(weights: dict[str, float], what: str) -> dict[str, float]:
    if not weights:
        raise ValueError(f"{what}: at least one entry is required")
    if any(w < 0 for w in weights.values()):
        raise ValueError(f"{what}: weights must be non-negative")
    total = sum(weights.values())
    if total <= 0:
        raise ValueError(f"{what}: weights sum to zero")
    return {k: v / total for k, v in weights.items()}


def from_dict(data: dict) -> Framework:
    items = int(data.get("items", 0))
    if items <= 0:
        raise ValueError("'items' must be a positive integer")
    raw = data.get("domains") or {}
    weights = _normalize({k: float(v["weight"]) for k, v in raw.items()}, "domains")
    domains = []
    for name, spec in raw.items():
        comps = spec.get("competencies") or {"General": 1.0}
        domains.append(Domain(
            name=name,
            weight=weights[name],
            min_items=int(spec.get("min_items", 0)),
            competencies=_normalize({k: float(v) for k, v in comps.items()}, f"{name} competencies"),
        ))
    if sum(d.min_items for d in domains) > items:
        raise ValueError("sum of min_items exceeds the number of items")
    levels = _normalize({k: float(v) for k, v in (data.get("cognitive_levels") or {"General": 1}).items()},
                        "cognitive_levels")
    return Framework(name=data.get("name", "Unnamed framework"), items=items,
                     domains=domains, cognitive_levels=levels)


def load(path: str | Path) -> Framework:
    with open(path, encoding="utf-8") as fh:
        return from_dict(yaml.safe_load(fh))
