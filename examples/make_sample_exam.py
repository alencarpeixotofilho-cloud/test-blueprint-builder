"""Create a fictitious finished exam that drifts a little from the blueprint,
so the alignment check has something to report."""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
plan = {
    "Internal Medicine": 31, "Surgery": 17, "Pediatrics": 21,
    "Obstetrics & Gynecology": 19, "Public Health": 12,
}
comps = {
    "Public Health": ["Epidemiology", "Health Systems", "Prevention"],
}
rows = []
for dom, n in plan.items():
    options = comps.get(dom, ["Diagnosis", "Management", "Prevention"])
    for _ in range(n):
        rows.append({
            "item_id": f"Q{len(rows) + 1:03d}",
            "domain": dom,
            "competency": rng.choice(options, p=None),
            "level": rng.choice(["Recall", "Application", "Analysis"], p=[0.32, 0.46, 0.22]),
        })
out = Path(__file__).parent / "exam_items.csv"
pd.DataFrame(rows).to_csv(out, index=False)
print(f"{len(rows)} items -> {out}")
