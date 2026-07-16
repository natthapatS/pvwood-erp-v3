"""Import the glue-BOM export CSV into GlueRecipe.

Stores each recipe's component quantities (kg) in `components`, plus total_kg,
mix_time, and applicability (veneer_thickness / wood_species / core_board).
Normalizes codes so the export's `Glue 9` matches the BOMs' `Glue 09`.
Idempotent (upsert by normalized code). Run from repo root:

    python -m scripts.import_glue_csv <path.csv>
"""
from __future__ import annotations

import csv
import re
import sys

from sqlmodel import Session, select

from app.db import engine
from app.models.bom import GlueRecipe
from scripts._import_utils import Report, num, s

COMPONENT_COLS = [
    "e0_glue_kg", "latex_g312_kg", "flour_kg", "yellow_pigment_kg", "hardener_kg",
    "red_pigment_kg", "black_pigment_kg", "titanium_kg",
]


def norm_code(code: str) -> str:
    """'Glue 9' -> 'Glue 09' so it matches the BOMs' zero-padded codes."""
    code = s(code)
    m = re.match(r"^(.*?)(\d+)$", code)
    if m:
        return f"{m.group(1)}{int(m.group(2)):02d}"
    return code


def run(path: str) -> None:
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    rep = Report()
    with Session(engine) as ses:
        recipes = {g.recipe_code: g for g in ses.exec(select(GlueRecipe)).all()}
        for i, row in enumerate(rows, start=2):
            code = norm_code(row.get("recipe_code"))
            if not code:
                rep.error("Glue", i, "missing recipe_code"); continue
            comps = {c.replace("_kg", ""): num(row.get(c))
                     for c in COMPONENT_COLS if num(row.get(c))}
            o = recipes.get(code) or GlueRecipe(recipe_code=code, name=code)
            o.name = s(row.get("name")) or o.name
            o.total_kg = num(row.get("total_kg")) or 0.0
            o.mix_time_min = int(num(row.get("mix_time_min")) or 20)
            o.veneer_thickness = s(row.get("veneer_thickness")) or None
            o.wood_species = s(row.get("wood_species")) or None
            o.core_board = s(row.get("core_board")) or None
            o.components = comps
            o.notes = s(row.get("notes"))
            if code not in recipes:
                ses.add(o); recipes[code] = o; rep.bump("Glue", "created")
            else:
                rep.bump("Glue", "updated")
        ses.commit()
    rep.print()


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "glue_bom_export.csv")
