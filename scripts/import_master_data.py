"""Import master data from templates/pvwood_master_data.xlsx into Postgres.

Sheets: WarehouseLocation, Supplier, Customer, Item. Idempotent (upsert by code).
Auto-masters species from the free-text Item.species; resolves supplier codes and
reports unknown references instead of guessing. Run from repo root:

    python -m scripts.import_master_data [path-to-xlsx]

(Glue recipes now live in the BOM workbook; logs are Items with kind=LOG.)
"""
from __future__ import annotations

import sys

from openpyxl import load_workbook
from sqlmodel import Session, select

from app.db import engine
from app.models.enums import ItemKind
from app.models.master import Item, Species, WarehouseLocation
from app.models.procurement import Supplier
from app.models.sales import Customer
from scripts._import_utils import Report, num, s, sheet_rows

DEFAULT_PATH = "templates/pvwood_master_data.xlsx"


def _cache(session: Session, model, key_attr: str) -> dict:
    return {getattr(o, key_attr): o for o in session.exec(select(model)).all()}


def run(path: str) -> None:
    wb = load_workbook(path, data_only=True)
    rep = Report()
    with Session(engine) as ses:
        locs = _cache(ses, WarehouseLocation, "code")
        sups = _cache(ses, Supplier, "code")
        custs = {c.name: c for c in ses.exec(select(Customer)).all()}
        items = _cache(ses, Item, "code")
        species = {sp.code: sp for sp in ses.exec(select(Species)).all()}

        def get_species(name: str) -> Species | None:
            name = s(name)
            if not name:
                return None
            code = name.upper()
            sp = species.get(code)
            if not sp:
                sp = Species(code=code, common_name=name)
                ses.add(sp)
                ses.flush()
                species[code] = sp
                rep.bump("Species", "auto-created")
            return sp

        # ── WarehouseLocation ──
        if "WarehouseLocation" in wb.sheetnames:
            for r, d in sheet_rows(wb["WarehouseLocation"]):
                code = s(d.get("code"))
                if not code:
                    rep.error("WarehouseLocation", r, "missing code"); continue
                o = locs.get(code) or WarehouseLocation(code=code, name=code)
                o.name = s(d.get("name")) or o.name
                o.kind = s(d.get("kind"))
                o.notes = s(d.get("notes"))
                if code not in locs:
                    ses.add(o); locs[code] = o; rep.bump("WarehouseLocation", "created")
                else:
                    rep.bump("WarehouseLocation", "updated")

        # ── Supplier ──
        if "Supplier" in wb.sheetnames:
            for r, d in sheet_rows(wb["Supplier"]):
                code = s(d.get("code"))
                if not code:
                    rep.error("Supplier", r, "missing code"); continue
                o = sups.get(code) or Supplier(code=code, name=code)
                o.name = s(d.get("name")) or o.name
                o.contact_person = s(d.get("contact_person"))
                o.phone = s(d.get("phone")); o.email = s(d.get("email"))
                o.address = s(d.get("address")); o.notes = s(d.get("notes"))
                if code not in sups:
                    ses.add(o); sups[code] = o; rep.bump("Supplier", "created")
                else:
                    rep.bump("Supplier", "updated")

        # ── Customer (keyed by name) ──
        if "Customer" in wb.sheetnames:
            for r, d in sheet_rows(wb["Customer"]):
                name = s(d.get("name"))
                if not name:
                    rep.error("Customer", r, "missing name"); continue
                o = custs.get(name) or Customer(name=name)
                o.contact_person = s(d.get("contact_person")); o.phone = s(d.get("phone"))
                o.email = s(d.get("email")); o.address = s(d.get("address"))
                o.notes = s(d.get("notes"))
                if name not in custs:
                    ses.add(o); custs[name] = o; rep.bump("Customer", "created")
                else:
                    rep.bump("Customer", "updated")

        ses.flush()

        # ── Item ──
        if "Item" in wb.sheetnames:
            valid_kinds = {k.value for k in ItemKind}
            for r, d in sheet_rows(wb["Item"]):
                code = s(d.get("code"))
                if not code:
                    rep.error("Item", r, "missing code"); continue
                kind = s(d.get("kind")).upper()
                if kind not in valid_kinds:
                    rep.error("Item", r, f"bad kind '{kind}' (allowed: {sorted(valid_kinds)})")
                    continue
                sup_code = s(d.get("supplier_code"))
                sup = sups.get(sup_code) if sup_code else None
                if sup_code and not sup:
                    rep.error("Item", r, f"unknown supplier_code '{sup_code}'"); continue
                sp = get_species(d.get("species"))
                o = items.get(code) or Item(code=code, name=code, kind=ItemKind(kind), unit="")
                o.kind = ItemKind(kind)
                o.name = s(d.get("name")) or o.name
                o.name_th = s(d.get("name_th")); o.name_zh = s(d.get("name_zh"))
                o.unit = s(d.get("unit")) or o.unit
                o.species_id = sp.id if sp else None
                o.grade = s(d.get("grade")) or None
                o.cut_type = s(d.get("cut_type")) or None
                o.matching = s(d.get("matching")) or None
                o.face_back = s(d.get("face_back")) or None
                o.fsc = s(d.get("fsc")) or None
                o.board_type = s(d.get("board_type")) or None
                o.glue_type = s(d.get("glue_type")) or None
                o.thickness_mm = num(d.get("thickness_mm"))
                o.width_mm = num(d.get("width_mm")); o.length_mm = num(d.get("length_mm"))
                o.unit_cost = num(d.get("unit_cost")) or 0.0
                o.price = num(d.get("price")) or 0.0
                o.acc_code = s(d.get("acc_code")) or None
                o.reorder_point = num(d.get("reorder_point")) or 0.0
                o.supplier_id = sup.id if sup else None
                o.notes = s(d.get("notes"))
                if code not in items:
                    ses.add(o); items[code] = o; rep.bump("Item", "created")
                else:
                    rep.bump("Item", "updated")

        ses.commit()
    rep.print()


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH)
