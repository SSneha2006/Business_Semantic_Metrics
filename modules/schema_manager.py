"""
Schema Management Module
Stores schemas and detects changes (add / remove / rename / modify).
"""

from __future__ import annotations
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any
from copy import deepcopy

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
SCHEMA_FILE = DATA_DIR / "schemas.json"
CHANGE_LOG_FILE = DATA_DIR / "schema_changes.json"


def _load_json(path: Path, default: Any) -> Any:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _save_json(path: Path, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def get_all_schemas() -> dict:
    return _load_json(SCHEMA_FILE, {})


def save_schema(source_name: str, tables: dict) -> dict:
    """
    tables format:
    {
      "orders": {
        "columns": {
          "order_id": {"type": "INTEGER", "nullable": False},
          "amount": {"type": "DECIMAL", "nullable": True},
          ...
        }
      },
      ...
    }
    """
    schemas = get_all_schemas()
    previous = schemas.get(source_name, {}).get("tables", {})
    fingerprint = _fingerprint(tables)

    schemas[source_name] = {
        "tables": tables,
        "fingerprint": fingerprint,
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    _save_json(SCHEMA_FILE, schemas)

    # Detect changes if previous version exists
    changes = []
    if previous:
        changes = detect_schema_changes(previous, tables)
        if changes:
            log_changes(source_name, changes)

    return {"source": source_name, "changes_detected": len(changes), "changes": changes}


def _fingerprint(tables: dict) -> str:
    raw = json.dumps(tables, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def detect_schema_changes(old_tables: dict, new_tables: dict) -> list[dict]:
    """
    Compare two schema snapshots and return a list of change events.
    Change types: ADDED_TABLE, REMOVED_TABLE, ADDED_COLUMN,
                  REMOVED_COLUMN, RENAMED_COLUMN (heuristic), MODIFIED_COLUMN
    """
    changes = []
    old_tnames = set(old_tables.keys())
    new_tnames = set(new_tables.keys())

    for t in new_tnames - old_tnames:
        changes.append({
            "type": "ADDED_TABLE",
            "table": t,
            "detail": f"Table '{t}' was added",
            "severity": "high",
        })

    for t in old_tnames - new_tnames:
        changes.append({
            "type": "REMOVED_TABLE",
            "table": t,
            "detail": f"Table '{t}' was removed",
            "severity": "critical",
        })

    for t in old_tnames & new_tnames:
        old_cols = old_tables[t].get("columns", {})
        new_cols = new_tables[t].get("columns", {})
        old_cnames = set(old_cols.keys())
        new_cnames = set(new_cols.keys())

        for c in new_cnames - old_cnames:
            # Heuristic: possible rename if similar name exists in removed
            possible_rename = _guess_rename(c, old_cnames - new_cnames)
            if possible_rename:
                changes.append({
                    "type": "RENAMED_COLUMN",
                    "table": t,
                    "old_column": possible_rename,
                    "new_column": c,
                    "detail": f"Column '{possible_rename}' may have been renamed to '{c}' in table '{t}'",
                    "severity": "high",
                })
            else:
                changes.append({
                    "type": "ADDED_COLUMN",
                    "table": t,
                    "column": c,
                    "detail": f"Column '{c}' added to table '{t}'",
                    "severity": "medium",
                })

        for c in old_cnames - new_cnames:
            # Only report as removed if not already treated as rename
            already_rename = any(
                ch.get("old_column") == c for ch in changes if ch["type"] == "RENAMED_COLUMN"
            )
            if not already_rename:
                changes.append({
                    "type": "REMOVED_COLUMN",
                    "table": t,
                    "column": c,
                    "detail": f"Column '{c}' removed from table '{t}'",
                    "severity": "critical",
                })

        for c in old_cnames & new_cnames:
            old_meta = old_cols[c]
            new_meta = new_cols[c]
            if old_meta.get("type") != new_meta.get("type") or old_meta.get("nullable") != new_meta.get("nullable"):
                changes.append({
                    "type": "MODIFIED_COLUMN",
                    "table": t,
                    "column": c,
                    "old": old_meta,
                    "new": new_meta,
                    "detail": f"Column '{c}' in '{t}' changed type/nullability",
                    "severity": "high",
                })

    return changes


def _guess_rename(new_col: str, removed_cols: set) -> str | None:
    """Simple heuristic: same letters ignoring underscores / case, or Levenshtein-ish."""
    n = new_col.lower().replace("_", "")
    for old in removed_cols:
        o = old.lower().replace("_", "")
        if n == o or (len(n) > 3 and (n in o or o in n)):
            return old
        # common patterns: amount → total_amount, revenue → net_revenue
        if n.endswith(o) or o.endswith(n):
            return old
    return None


def log_changes(source_name: str, changes: list[dict]) -> None:
    log = _load_json(CHANGE_LOG_FILE, [])
    entry = {
        "source": source_name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "changes": changes,
    }
    log.append(entry)
    _save_json(CHANGE_LOG_FILE, log)


def get_change_log(limit: int = 50) -> list:
    log = _load_json(CHANGE_LOG_FILE, [])
    return list(reversed(log[-limit:]))


def get_current_schema(source_name: str) -> dict:
    schemas = get_all_schemas()
    return schemas.get(source_name, {}).get("tables", {})


# ---------- Sample / Demo data ----------

def seed_demo_schema() -> None:
    """Load a realistic e-commerce style schema for demos."""
    demo = {
        "orders": {
            "columns": {
                "order_id": {"type": "INTEGER", "nullable": False},
                "customer_id": {"type": "INTEGER", "nullable": False},
                "order_date": {"type": "DATE", "nullable": False},
                "gross_amount": {"type": "DECIMAL", "nullable": False},
                "discount": {"type": "DECIMAL", "nullable": True},
                "tax": {"type": "DECIMAL", "nullable": True},
                "status": {"type": "VARCHAR", "nullable": False},
            }
        },
        "customers": {
            "columns": {
                "customer_id": {"type": "INTEGER", "nullable": False},
                "name": {"type": "VARCHAR", "nullable": False},
                "email": {"type": "VARCHAR", "nullable": True},
                "signup_date": {"type": "DATE", "nullable": False},
                "region": {"type": "VARCHAR", "nullable": True},
            }
        },
        "products": {
            "columns": {
                "product_id": {"type": "INTEGER", "nullable": False},
                "product_name": {"type": "VARCHAR", "nullable": False},
                "category": {"type": "VARCHAR", "nullable": True},
                "unit_price": {"type": "DECIMAL", "nullable": False},
            }
        },
        "order_items": {
            "columns": {
                "item_id": {"type": "INTEGER", "nullable": False},
                "order_id": {"type": "INTEGER", "nullable": False},
                "product_id": {"type": "INTEGER", "nullable": False},
                "quantity": {"type": "INTEGER", "nullable": False},
                "unit_price": {"type": "DECIMAL", "nullable": False},
            }
        },
    }
    save_schema("demo_ecommerce", demo)


def apply_demo_schema_change(variant: str = "rename_discount") -> list[dict]:
    """
    Simulate common schema evolution scenarios for the demo.
    Returns the list of detected changes.
    """
    current = get_current_schema("demo_ecommerce")
    if not current:
        seed_demo_schema()
        current = get_current_schema("demo_ecommerce")

    new_tables = deepcopy(current)

    if variant == "rename_discount":
        # Simulate: discount → discount_amount
        if "discount" in new_tables["orders"]["columns"]:
            meta = new_tables["orders"]["columns"].pop("discount")
            new_tables["orders"]["columns"]["discount_amount"] = meta

    elif variant == "remove_tax":
        new_tables["orders"]["columns"].pop("tax", None)

    elif variant == "add_shipping":
        new_tables["orders"]["columns"]["shipping_cost"] = {
            "type": "DECIMAL",
            "nullable": True,
        }

    elif variant == "change_type":
        if "quantity" in new_tables.get("order_items", {}).get("columns", {}):
            new_tables["order_items"]["columns"]["quantity"]["type"] = "BIGINT"

    elif variant == "add_table":
        new_tables["returns"] = {
            "columns": {
                "return_id": {"type": "INTEGER", "nullable": False},
                "order_id": {"type": "INTEGER", "nullable": False},
                "reason": {"type": "VARCHAR", "nullable": True},
                "refund_amount": {"type": "DECIMAL", "nullable": False},
            }
        }

    result = save_schema("demo_ecommerce", new_tables)
    return result.get("changes", [])
