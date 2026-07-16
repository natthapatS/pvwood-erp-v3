"""Shared helpers for the Excel importers."""
from __future__ import annotations


def s(v) -> str:
    """Trimmed string ('' for blanks)."""
    return "" if v is None else str(v).strip()


def num(v) -> float | None:
    v = s(v).replace(",", "")
    if not v or v in ("-", "NON", "N/A", "na"):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def intnum(v) -> int | None:
    f = num(v)
    return int(f) if f is not None else None


def sheet_rows(ws, example=None):
    """Yield (excel_row_number, {header: value}) for non-blank data rows (row 2+).

    Skips a row that exactly matches the template's built-in `example` (older
    templates shipped an example row; robust either way).
    """
    if example is None:
        try:
            from scripts.build_templates import EXAMPLES
            example = EXAMPLES.get(ws.title)
        except Exception:
            example = None
    headers = [s(c.value).replace("★", "").strip() for c in ws[1]]
    ex = [s(x) for x in example] if example else None
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        vals = [s(v) for v in row]
        if all(v == "" for v in vals):
            continue
        if ex is not None and vals[: len(ex)] == ex:
            continue
        yield i, {h: v for h, v in zip(headers, row) if h}


class Report:
    """Collects per-sheet counts + errors and prints a summary."""

    def __init__(self) -> None:
        self.counts: dict[str, dict[str, int]] = {}
        self.errors: list[str] = []

    def bump(self, sheet: str, key: str, n: int = 1) -> None:
        self.counts.setdefault(sheet, {}).setdefault(key, 0)
        self.counts[sheet][key] += n

    def error(self, sheet: str, row: int, msg: str) -> None:
        self.errors.append(f"  {sheet} row {row}: {msg}")

    def print(self) -> None:
        print("\n=== import summary ===")
        for sheet, c in self.counts.items():
            print(f"  {sheet}: " + ", ".join(f"{k}={v}" for k, v in c.items()))
        if self.errors:
            print(f"\n=== {len(self.errors)} error(s) (rows skipped) ===")
            for e in self.errors:
                print(e)
        else:
            print("\nno errors.")
