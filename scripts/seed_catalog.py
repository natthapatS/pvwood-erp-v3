"""Seed the line / department / station catalog from canonical defaults.

Idempotent — safe to re-run (upserts; replaces line_flow for known lines).
Run from the repo root:  python -m scripts.seed_catalog
"""
from sqlmodel import Session, select

from app.db import engine
from app.models.catalog import Department, LineFlow, ManufacturingLine, Station

# (line_id, label, line_type, sort_order)
LINES = [
    ("FC", "Feed Center", "prep", 0),
    ("P01", "Production Line 01", "main", 1),
    ("P02", "Production Line 02", "main", 2),
    ("P37", "Production Line 37", "main", 3),
    ("PUV", "UV Line", "aux", 10),
    ("PVS", "Veneer Slicing", "aux", 11),
    ("PSP", "Veneer Splicing", "aux", 12),
]

# (code, label, icon, is_centralised, sort_order)
DEPARTMENTS = [
    ("fc", "Feed Center", "bi-box-seam", False, 1),
    ("laminating", "Glue & Laminating", "bi-layers", False, 2),
    ("cold_press", "Cold Press", "bi-snow", False, 3),
    ("hot_press", "Hot Press", "bi-fire", False, 4),
    ("bleach", "Bleach", "bi-droplet", False, 5),
    ("repair", "Repair", "bi-tools", False, 6),
    ("sanding", "Sanding", "bi-circle-half", False, 7),
    ("grading", "Grading", "bi-stars", False, 8),
    ("packing", "Packing", "bi-box", True, 9),
    ("fg_receiving", "FG Receiving", "bi-inbox", True, 10),
    ("fg_warehouse", "FG Warehouse", "bi-building", True, 11),
]

_MAIN_FLOW = ["laminating", "cold_press", "hot_press", "bleach", "repair",
              "sanding", "grading", "packing", "fg_warehouse"]
# Aux lines (PUV/PVS/PSP) intentionally have no flow (transform/request hubs).
FLOW = {"FC": ["fc"], "P01": _MAIN_FLOW, "P02": _MAIN_FLOW, "P37": _MAIN_FLOW}


def seed() -> None:
    dept_label = {c: label for c, label, *_ in DEPARTMENTS}
    centralised = {c for c, _, _, cent, _ in DEPARTMENTS if cent}

    with Session(engine) as s:
        for line_id, label, ltype, order in LINES:
            row = s.get(ManufacturingLine, line_id)
            if row:
                row.label, row.line_type, row.sort_order = label, ltype, order
            else:
                s.add(ManufacturingLine(line_id=line_id, label=label,
                                        line_type=ltype, sort_order=order))

        for code, label, icon, cent, order in DEPARTMENTS:
            row = s.get(Department, code)
            if row:
                row.label, row.icon, row.is_centralised, row.sort_order = (
                    label, icon, cent, order)
            else:
                s.add(Department(code=code, label=label, icon=icon,
                                 is_centralised=cent, sort_order=order))
        s.commit()

        # line_flow: replace rows for the known lines
        for line_code, depts in FLOW.items():
            for lf in s.exec(select(LineFlow).where(LineFlow.line_code == line_code)).all():
                s.delete(lf)
            for i, dept in enumerate(depts):
                s.add(LineFlow(line_code=line_code, seq=i, department_code=dept))
        s.commit()

        # stations: one per (line, per-line dept); fc only on the FC line
        for line_code, depts in FLOW.items():
            for dept in depts:
                if dept in centralised:
                    continue
                if dept == "fc" and line_code != "FC":
                    continue
                label = f"{line_code} · {dept_label.get(dept, dept)}"
                existing = s.exec(
                    select(Station).where(
                        Station.line_code == line_code,
                        Station.department_code == dept,
                    )
                ).first()
                if existing:
                    existing.label = label
                else:
                    s.add(Station(line_code=line_code, department_code=dept, label=label))
        # centralised depts: one line-less station each
        for dept in centralised:
            existing = s.exec(
                select(Station).where(
                    Station.line_code.is_(None),
                    Station.department_code == dept,
                )
            ).first()
            if not existing:
                s.add(Station(line_code=None, department_code=dept,
                              label=dept_label.get(dept, dept)))
        s.commit()

    print("catalog seeded")


if __name__ == "__main__":
    seed()
