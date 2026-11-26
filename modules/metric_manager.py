"""
Metric Management + Semantic Layer Module
Central store of business metric definitions with validation & lineage.
"""

from __future__ import annotations
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from copy import deepcopy

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
METRICS_FILE = DATA_DIR / "metrics.json"


def _load_json(path: Path, default: Any) -> Any:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _save_json(path: Path, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def get_all_metrics() -> dict:
    return _load_json(METRICS_FILE, {})


def get_metric(name: str) -> dict | None:
    return get_all_metrics().get(name)


def save_metric(metric: dict) -> dict:
    """
    Expected metric structure:
    {
      "name": "Revenue",
      "description": "...",
      "expression": "SUM(orders.gross_amount - COALESCE(orders.discount, 0))",
      "tables": ["orders"],
      "columns": ["orders.gross_amount", "orders.discount"],
      "dimensions": ["orders.order_date", "customers.region"],
      "owner": "Finance",
      "tags": ["financial", "kpi"],
      "status": "active" | "draft" | "deprecated",
      "created_at": "...",
      "updated_at": "..."
    }
    """
    metrics = get_all_metrics()
    name = metric["name"].strip()
    now = datetime.utcnow().isoformat() + "Z"

    if name in metrics:
        metric["created_at"] = metrics[name].get("created_at", now)
        metric["updated_at"] = now
        metric["version"] = metrics[name].get("version", 1) + 1
    else:
        metric["created_at"] = now
        metric["updated_at"] = now
        metric["version"] = 1

    # Auto-extract referenced columns/tables from expression if not supplied
    if not metric.get("columns"):
        metric["columns"] = _extract_columns(metric.get("expression", ""))
    if not metric.get("tables"):
        metric["tables"] = list({c.split(".")[0] for c in metric["columns"] if "." in c})

    metrics[name] = metric
    _save_json(METRICS_FILE, metrics)
    return metric


def delete_metric(name: str) -> bool:
    metrics = get_all_metrics()
    if name in metrics:
        del metrics[name]
        _save_json(METRICS_FILE, metrics)
        return True
    return False


def _extract_columns(expression: str) -> list[str]:
    """Very simple parser: look for table.column patterns."""
    pattern = r"\b([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)\b"
    return sorted(set(re.findall(pattern, expression)))


def validate_metric(metric: dict, schema: dict) -> dict:
    """
    Validate that a metric definition is compatible with the current schema.
    Returns {valid: bool, errors: [], warnings: []}
    """
    errors = []
    warnings = []

    name = metric.get("name", "").strip()
    if not name:
        errors.append("Metric name is required")
    if not metric.get("expression"):
        errors.append("Expression is required")

    expression = metric.get("expression", "")
    columns = metric.get("columns") or _extract_columns(expression)
    tables = metric.get("tables") or list({c.split(".")[0] for c in columns if "." in c})

    for t in tables:
        if t not in schema:
            errors.append(f"Table '{t}' does not exist in current schema")
            continue
        schema_cols = schema[t].get("columns", {})
        for col_ref in columns:
            if not col_ref.startswith(t + "."):
                continue
            col = col_ref.split(".", 1)[1]
            if col not in schema_cols:
                errors.append(f"Column '{col}' not found in table '{t}'")
            else:
                # Type warning for non-numeric columns in aggregations
                col_type = schema_cols[col].get("type", "").upper()
                if any(agg in expression.upper() for agg in ["SUM(", "AVG(", "COUNT("]):
                    if col_type in ("VARCHAR", "TEXT", "DATE", "BOOLEAN") and "COUNT(" not in expression.upper():
                        warnings.append(
                            f"Column '{col}' has type {col_type}; may be unsuitable for numeric aggregation"
                        )

    # Expression basic sanity
    if expression.count("(") != expression.count(")"):
        errors.append("Unbalanced parentheses in expression")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "referenced_columns": columns,
        "referenced_tables": tables,
    }


def impact_analysis(schema_changes: list[dict], metrics: dict | None = None) -> list[dict]:
    """
    Given a list of schema changes, return which metrics are affected and how.
    """
    if metrics is None:
        metrics = get_all_metrics()

    impacted = []
    for mname, metric in metrics.items():
        m_cols = set(metric.get("columns") or _extract_columns(metric.get("expression", "")))
        m_tables = set(metric.get("tables") or [])

        reasons = []
        severity = "low"

        for ch in schema_changes:
            ctype = ch["type"]
            table = ch.get("table")
            col = ch.get("column") or ch.get("old_column")

            if ctype == "REMOVED_TABLE" and table in m_tables:
                reasons.append(f"Depends on removed table '{table}'")
                severity = "critical"
            elif ctype == "REMOVED_COLUMN" and f"{table}.{col}" in m_cols:
                reasons.append(f"Depends on removed column '{table}.{col}'")
                severity = "critical"
            elif ctype == "RENAMED_COLUMN":
                old_ref = f"{table}.{ch.get('old_column')}"
                if old_ref in m_cols:
                    reasons.append(
                        f"Depends on renamed column '{ch.get('old_column')}' → '{ch.get('new_column')}'"
                    )
                    severity = "high" if severity != "critical" else severity
            elif ctype == "MODIFIED_COLUMN" and f"{table}.{col}" in m_cols:
                reasons.append(f"Column '{table}.{col}' type/nullability changed")
                severity = "high" if severity != "critical" else severity
            elif ctype == "ADDED_COLUMN":
                # informational only
                pass

        if reasons:
            impacted.append({
                "metric": mname,
                "severity": severity,
                "reasons": reasons,
                "expression": metric.get("expression"),
                "owner": metric.get("owner", "—"),
                "status": metric.get("status", "active"),
            })

    # Sort critical first
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    impacted.sort(key=lambda x: order.get(x["severity"], 9))
    return impacted


def get_lineage(metric_name: str) -> dict:
    """Return simple lineage graph data for a metric."""
    metric = get_metric(metric_name)
    if not metric:
        return {}
    columns = metric.get("columns") or _extract_columns(metric.get("expression", ""))
    tables = metric.get("tables") or list({c.split(".")[0] for c in columns if "." in c})

    nodes = [{"id": metric_name, "type": "metric", "label": metric_name}]
    edges = []
    for t in tables:
        nodes.append({"id": t, "type": "table", "label": t})
        edges.append({"from": t, "to": metric_name, "label": "feeds"})
    for c in columns:
        nodes.append({"id": c, "type": "column", "label": c})
        table = c.split(".")[0] if "." in c else None
        if table:
            edges.append({"from": c, "to": table, "label": "belongs"})
            edges.append({"from": c, "to": metric_name, "label": "used by"})

    return {
        "metric": metric_name,
        "expression": metric.get("expression"),
        "nodes": nodes,
        "edges": edges,
        "tables": tables,
        "columns": columns,
    }


# ---------- Seed demo metrics ----------

def seed_demo_metrics() -> None:
    demos = [
        {
            "name": "Revenue",
            "description": "Net revenue after discounts (canonical definition)",
            "expression": "SUM(orders.gross_amount - COALESCE(orders.discount, 0))",
            "tables": ["orders"],
            "columns": ["orders.gross_amount", "orders.discount"],
            "dimensions": ["orders.order_date", "customers.region"],
            "owner": "Finance",
            "tags": ["financial", "kpi", "revenue"],
            "status": "active",
        },
        {
            "name": "Gross Sales",
            "description": "Total gross sales before any discounts",
            "expression": "SUM(orders.gross_amount)",
            "tables": ["orders"],
            "columns": ["orders.gross_amount"],
            "dimensions": ["orders.order_date"],
            "owner": "Finance",
            "tags": ["financial", "kpi"],
            "status": "active",
        },
        {
            "name": "Average Order Value",
            "description": "Average order value after discounts",
            "expression": "AVG(orders.gross_amount - COALESCE(orders.discount, 0))",
            "tables": ["orders"],
            "columns": ["orders.gross_amount", "orders.discount"],
            "dimensions": ["orders.order_date"],
            "owner": "Analytics",
            "tags": ["kpi", "orders"],
            "status": "active",
        },
        {
            "name": "Customer Count",
            "description": "Distinct customers who placed at least one order",
            "expression": "COUNT(DISTINCT orders.customer_id)",
            "tables": ["orders"],
            "columns": ["orders.customer_id"],
            "dimensions": ["customers.region"],
            "owner": "Marketing",
            "tags": ["customers", "kpi"],
            "status": "active",
        },
        {
            "name": "Total Tax Collected",
            "description": "Sum of tax amounts on orders",
            "expression": "SUM(orders.tax)",
            "tables": ["orders"],
            "columns": ["orders.tax"],
            "dimensions": ["orders.order_date"],
            "owner": "Finance",
            "tags": ["financial", "tax"],
            "status": "active",
        },
        {
            "name": "Items Sold",
            "description": "Total quantity of items sold",
            "expression": "SUM(order_items.quantity)",
            "tables": ["order_items"],
            "columns": ["order_items.quantity"],
            "dimensions": ["products.category"],
            "owner": "Operations",
            "tags": ["operations", "volume"],
            "status": "active",
        },
    ]
    for m in demos:
        if not get_metric(m["name"]):
            save_metric(m)
