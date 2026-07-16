# Production logs & lines — v3 requirements

Authoritative spec for the Production domain (5) and the aux-line transformation
model. Captured from the owner design session (2026-07). Feeds BOM (domain 2),
RM Lot (4), Traceability (6), FG (8), Cost (11).

## Lines
- **FC** — Feed Center (material prep / QC / staging; not a production stage).
- **Main lines P01 / P02 / P37** — full department flow, one StationRecord per stage.
- **Aux lines PUV / PVS / PSP** — material *transformations* (multi-step runs that
  consume input lot(s) and produce output lot(s) with genealogy + per-step loss).

## Main-line station logs (confirmed accurate — carry over)
Per batch: **pcs_in / pcs_out (or target/actual) + operator(s) + machine + time +
station-specific process fields + notes**.

| Station | Station-specific fields |
|---|---|
| Glue & Laminating | table, 2 operators, glue-mix ref, pcs target/actual, g/face, time |
| Cold Press | machine, operator, pressure (bar), dwell (min), pcs in/out |
| Hot Press | machine, operator, temp (°C), pressure, press time, pcs in/out |
| Repair | table, type (ROUGH/FINE), 2 operators, pcs repaired |
| Sanding | machine, operator, grit, feed speed, pcs in/out, defect count |
| Grading | grader, outcome (PASS/PARTIAL_NCG/FULL_NCG/REJECT), pcs A/B/NCG/reject, NCG reason |
| Packing | operator, table, pcs in/packed/held, cartons, packaging SKU |
| Bleach | (in flow; no legacy fields — core only for now) |

**Model:** single `StationRecord` (core columns) + `params` JSONB for the
station-specific fields. Grading's grade split feeds FG lots + TAS 2 grade costing.

## Aux-line transformations

### PVS — Veneer Slicing (logs → veneer)
- **Intake:** logs, measured in **m³** (new raw material; tracked per log lot).
- **Steps (per-step loss tracked):** ① heat/condition in vat → ② sawmill → flitch
  (**sawmill loss**) → ③ slice → veneer → ④ pack to pallets.
- **Output:** veneer in **m²**, under the **SAME item code as the equivalent bought
  veneer** (matching cut / species / grade) — interchangeable in stock; delivered to FC.
- **Report:** yield **m² veneer per m³ log**, traced to each log lot.

### PSP — Veneer Splicing (bought veneer → spliced pcs)
- **Intake:** bought veneer in **m²** (from lots).
- **Steps:** ① cut head length + width to size → ② splice into **pcs** (standard W×L)
  → ③ **grade**.
- **Output:** spliced veneer **pcs, per grade** — each grade is a new lot, traced back
  to the input m² veneer lots (grade-distributed genealogy).

### PUV — UV Line (one flexible run, `mode` flag)
- **Mode A — Primed door skin (produces FG):** raw board + sealer + primer → apply in
  3 stages → prepare + grade → pack → **FG to FGWH**.
- **Mode B — UV topcoat (P01 detour):** WIP from P01 grading → UV topcoat (1- or
  2-side) → **return to P01** for grading + packing → FGWH.
- Input may be a **raw lot** or a **P01 WIP batch** (polymorphic input).

## UNIFIED MODEL (owner decision 2026-07 — supersedes the transformation-run design)

Every line — main (P01/P02/P37) **and aux (PVS/PSP/PUV)** — runs **one production
engine**: a `ProductionBatch` moves through the ordered departments of its line's
`line_flow` (the **Kanban** board), and each stage is logged in `StationRecord` (the
**Station Hub**). Movement is **free-form** (`BatchMovement` ledger); `line_flow` just
defines the expected route + Kanban columns.

- **Aux stages are catalog departments + line_flow** (seeded, DB-editable):
  - PVS: `vat_heating → sawmill → slicing → double_edge_trim` (grade folded into trim)
  - PSP: `trimming → edge_gluing → splicing → repair → grading`
  - PUV Mode A: `sealer → primer_1 → primer_2 → grading → packing → fg_warehouse`
    (3 separate coat stations, each logged per pass)
  - PUV Mode B: a single `uv_topcoat` station (P01 panels detour in from grading, back out)
- `current_department` / `StationRecord.department` are catalog dept **strings** (not a
  fixed enum), so new stages need no schema change.
- **The separate transformation-run tables were dropped** (`TransformationRun`,
  `LogProcessing`, `SplicingRecord`, `FinishingJob`). Per-stage yields/losses (sawing
  loss, veneer m²/log, sheet count, 2-pass g/m²) live in `StationRecord.params`.
- **Yield recipe kept** (`TransformationRecipe`/`TransformationRecipeLine`, domain 2b):
  the one-input → many-graded-outputs shape a normal product BOM can't express
  (log in → veneer grades A/B/C out, with expected yield%). This is the `Transform_PVS/PSP`
  template (INPUT/OUTPUT rows only — stages moved to the catalog).
- Genealogy: log/lot → batch → output veneer lots via `LotLinkage` (domain 6).
- Logs still intake in **m³**; `Log`/`LogArrival`/`LogDocument` + `HeatingVat` kept.
