"""Import an Item master CSV (legacy materials export) into Postgres.

Auto-detects kind (VENEER if the file has a `species` column, else BOARD),
auto-masters Species (veneers) and Suppliers (from the free-text supplier name),
maps min_stock -> reorder_point, and ignores the stock columns (v3 derives
on-hand from lots). Idempotent (upsert by code). Run from repo root:

    python -m scripts.import_items_csv <path.csv> [KIND]
"""
from __future__ import annotations

import csv
import sys

from sqlmodel import Session, select

from app.db import engine
from app.models.enums import ItemKind
from app.models.master import Item, Species
from app.models.procurement import Supplier
from scripts._import_utils import Report, num, s


def clean(v) -> str:
    v = s(v)
    return "" if v == "-" else v


def run(path: str, kind_arg: str | None = None) -> None:
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("empty file"); return
    headers = set(rows[0].keys())
    kind = (ItemKind(kind_arg.upper()) if kind_arg
            else ItemKind.VENEER if "species" in headers else ItemKind.BOARD)
    rep = Report()
    sheet = f"CSV({kind.value})"

    with Session(engine) as ses:
        items = {i.code: i for i in ses.exec(select(Item)).all()}
        species = {sp.code: sp for sp in ses.exec(select(Species)).all()}
        sups = {sp.name: sp for sp in ses.exec(select(Supplier)).all()}
        sup_seq = [len(ses.exec(select(Supplier)).all())]

        def get_species(name: str):
            name = clean(name)
            if not name:
                return None
            code = name.upper()
            sp = species.get(code)
            if not sp:
                sp = Species(code=code, common_name=name)
                ses.add(sp); ses.flush(); species[code] = sp; rep.bump(sheet, "species+")
            return sp

        def get_supplier(name: str):
            name = clean(name)
            if not name:
                return None
            sp = sups.get(name)
            if not sp:
                sup_seq[0] += 1
                sp = Supplier(code=f"SUP{sup_seq[0]:04d}", name=name)
                ses.add(sp); ses.flush(); sups[name] = sp; rep.bump(sheet, "supplier+")
            return sp

        for i, row in enumerate(rows, start=2):
            code = clean(row.get("code"))
            if not code:
                rep.error(sheet, i, "missing code"); continue
            sp = get_species(row.get("species"))
            sup = get_supplier(row.get("supplier"))
            o = items.get(code) or Item(code=code, name=code, kind=kind, unit="")
            o.kind = kind
            o.name = clean(row.get("name")) or o.name
            o.name_th = clean(row.get("name_th"))
            o.acc_code = clean(row.get("acc_code")) or None
            o.unit = clean(row.get("unit")) or o.unit
            o.species_id = sp.id if sp else None
            o.grade = clean(row.get("grade")) or None
            o.cut_type = clean(row.get("cut_type")) or None
            o.matching = clean(row.get("matching")) or None
            o.face_back = clean(row.get("face_back")) or None
            o.fsc = clean(row.get("fsc")) or None
            o.board_type = clean(row.get("board_type")) or None
            o.glue_type = clean(row.get("glue_type")) or None
            o.auto_glue_code = clean(row.get("auto_glue_code")) or None
            o.thickness_mm = num(row.get("thickness_mm"))
            o.width_mm = num(row.get("width_mm"))
            o.length_mm = num(row.get("length_mm"))
            o.unit_cost = num(row.get("unit_cost")) or 0.0
            o.reorder_point = num(row.get("min_stock")) or 0.0
            o.supplier_id = sup.id if sup else None
            if code not in items:
                ses.add(o); items[code] = o; rep.bump(sheet, "created")
            else:
                rep.bump(sheet, "updated")
        ses.commit()
    rep.print()


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
