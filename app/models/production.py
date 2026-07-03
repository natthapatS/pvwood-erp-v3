"""Domain 5 — Production.

Planned (Phase 1): ProductionOrder (<- production_orders), ProductionBatch
(<- batches), StationRecord (consolidates the 7 *_log/*_records station tables),
RMIssue (<- batch_material_lots / station_stock_movements).

OPEN ITEM: PUV / PVS / PSP per-line production-procedure logs — raise with owner
before finalizing StationRecord.
"""
