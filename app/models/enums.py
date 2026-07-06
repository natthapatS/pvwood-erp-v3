"""Domain 0 — Enums.

The five enums named in the Domain Map (MovementType, GradeCode, OrderStatus,
StationCode, BatchStatus) plus a couple of supporting ones. Values are grounded
in the legacy app's actual status/grade strings (uppercased/cleaned), not
invented. Domain models bind these to PostgreSQL enum types.

PROVISIONAL: GradeCode and the grade/station vocab are business-specific — confirm
the full set with the owner at the FC/QA and Production stages.
"""
import enum


class MovementType(str, enum.Enum):
    """Kinds of stock / lot movement recorded in the LotMovement ledger.

    The transform types (GRADE / SPLICE / CUT_RESIZE) are what let a lot code
    identify internally-produced material with parent->child genealogy (Stage 2a).
    """

    RECEIVE = "RECEIVE"        # goods receipt into a lot
    TRANSFER = "TRANSFER"      # location/department move
    ADJUST = "ADJUST"          # stock-take / correction
    CONSUME = "CONSUME"        # issued into a production batch
    PRODUCE = "PRODUCE"        # output produced (e.g. FG lot)
    GRADE = "GRADE"            # transform: reclassify veneer to a new grade
    SPLICE = "SPLICE"          # transform: splice veneers into a new lot
    CUT_RESIZE = "CUT_RESIZE"  # transform: cut a board into smaller lots
    SHIP = "SHIP"              # dispatch out
    SCRAP = "SCRAP"            # written off


class GradeCode(str, enum.Enum):
    """Veneer / panel grade classification (PROVISIONAL — confirm full set)."""

    LG = "LG"    # legacy grading_records.grade_lg
    C = "C"      # legacy grading_records.grade_c
    NCG = "NCG"  # non-conforming goods


class GradeOutcome(str, enum.Enum):
    """Outcome of a grading pass (legacy grading_log.grade_outcome)."""

    PASS = "PASS"
    PARTIAL_NCG = "PARTIAL_NCG"
    FULL_NCG = "FULL_NCG"
    REJECT = "REJECT"


class OrderStatus(str, enum.Enum):
    """Lifecycle superset covering sales + production orders.

    Grounded in legacy values: orders (pending/in_progress), production_orders
    (planned/in_progress), purchase_orders (open/in_production/partial/released/
    cancelled).
    """

    DRAFT = "DRAFT"
    PENDING = "PENDING"
    PLANNED = "PLANNED"
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    PARTIAL = "PARTIAL"
    RELEASED = "RELEASED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class BatchStatus(str, enum.Enum):
    """Production batch lifecycle (legacy batches.status: active/completed/ncg)."""

    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    SPLIT = "SPLIT"
    NCG = "NCG"
    COMPLETED = "COMPLETED"
    SCRAPPED = "SCRAPPED"


class RequestStatus(str, enum.Enum):
    """Fulfilment status for move / consumable / purchase requests."""

    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class StationCode(str, enum.Enum):
    """Department / station codes (values match the legacy `departments.code`).

    Per-line departments run once per manufacturing line; the last three are
    centralised (one instance for all lines).
    """

    FC = "fc"                    # Feed Center (material prep / QC / staging)
    LAMINATING = "laminating"    # Glue & Laminating (glue_mix merged in)
    COLD_PRESS = "cold_press"
    HOT_PRESS = "hot_press"
    BLEACH = "bleach"
    REPAIR = "repair"
    SANDING = "sanding"
    GRADING = "grading"
    PACKING = "packing"              # centralised
    FG_RECEIVING = "fg_receiving"    # centralised
    FG_WAREHOUSE = "fg_warehouse"    # centralised


class ItemKind(str, enum.Enum):
    """Discriminator for the polymorphic Item catalog (<- legacy materials.type)."""

    VENEER = "VENEER"
    BOARD = "BOARD"
    GLUE_COMPONENT = "GLUE_COMPONENT"
    CONSUMABLE = "CONSUMABLE"
    PACKING = "PACKING"
    OTHER = "OTHER"


class CalcMethod(str, enum.Enum):
    """BOM quantity basis (<- legacy bom_groups.calc_method)."""

    PER_SHEET = "PER_SHEET"
    PER_PALLET = "PER_PALLET"


class BOMType(str, enum.Enum):
    """Assembly BOM (main-line product) vs transformation BOM (aux line)."""

    ASSEMBLY = "ASSEMBLY"            # P01/P02/P37: board + veneers + glue -> product
    TRANSFORMATION = "TRANSFORMATION"  # PUV/PVS/PSP: input lot(s) -> output lot(s)


class BOMLineRole(str, enum.Enum):
    """Role of a BOM line (<- legacy bom_lines seq semantics)."""

    BOARD = "BOARD"              # seq 1 (base board)
    FACE_VENEER = "FACE_VENEER"  # seq 2
    BACK_VENEER = "BACK_VENEER"  # seq 3
    FACE_GLUE = "FACE_GLUE"      # seq 4
    BACK_GLUE = "BACK_GLUE"      # seq 5
    PACKING = "PACKING"
    INPUT = "INPUT"              # transformation input (aux lines)
    OUTPUT = "OUTPUT"            # transformation output (aux lines)
    OTHER = "OTHER"
