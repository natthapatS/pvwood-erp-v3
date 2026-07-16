"""Domain 1c — Logs (retired 2026-07).

Logs are no longer a separate entity. A log *type* is an Item (kind=LOG, e.g.
"LRO4S"); each physical log is a RawMaterialLot of that item (its volume is the
lot's m³ quantity; container/traceability lives on the lot at receiving). The
former LogArrival / Log / LogDocument tables were dropped.
"""
