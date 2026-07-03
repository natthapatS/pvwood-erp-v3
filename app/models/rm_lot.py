"""Domain 4 — RM lot tracking.

Planned (Phase 1): RawMaterialLot (<- material_lots), LotMovement (unified ledger).

Stage 2a: LotMovement becomes the single ledger for RECEIVE / TRANSFER / ADJUST /
CONSUME and internal transforms GRADE / SPLICE / CUT_RESIZE (folding
veneer_regrade_log + board_resize_log + grading splits into parent->child lot
events with cost flow). Lot code = universal traceability key.
"""
