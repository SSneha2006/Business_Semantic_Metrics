"""
AI-Assisted Metric Definition Helper
Provides intelligent suggestions for metric expressions, descriptions,
and natural-language → metric conversion using rule-based + pattern AI.
(Designed to be easily replaceable with a real LLM API later.)
"""

from __future__ import annotations
import re
from typing import Any


# Common business metric patterns (knowledge base)
METRIC_PATTERNS = [
    {
        "keywords": ["revenue", "net revenue", "net sales"],
        "name": "Revenue",
        "expression_template": "SUM({amount_col} - COALESCE({discount_col}, 0))",
        "description": "Net revenue after discounts (canonical definition)",
        "preferred_cols": {
            "amount_col": ["gross_amount", "amount", "sales", "total_amount", "revenue"],
            "discount_col": ["discount", "discount_amount", "disc"],
        },
        "owner": "Finance",
        "tags": ["financial", "kpi", "revenue"],
    },
    {
        "keywords": ["gross sales", "gross revenue", "total sales"],
        "name": "Gross Sales",
        "expression_template": "SUM({amount_col})",
        "description": "Total gross sales before discounts",
        "preferred_cols": {
            "amount_col": ["gross_amount", "amount", "sales", "total_amount"],
        },
        "owner": "Finance",
        "tags": ["financial", "kpi"],
    },
    {
        "keywords": ["aov", "average order value", "avg order value"],
        "name": "Average Order Value",
        "expression_template": "AVG({amount_col} - COALESCE({discount_col}, 0))",
        "description": "Average order value after discounts",
        "preferred_cols": {
            "amount_col": ["gross_amount", "amount", "total_amount"],
            "discount_col": ["discount", "discount_amount"],
        },
        "owner": "Analytics",
        "tags": ["kpi", "orders"],
    },
    {
        "keywords": ["customer count", "unique customers", "number of customers"],
        "name": "Customer Count",
        "expression_template": "COUNT(DISTINCT {customer_col})",
        "description": "Distinct customers who placed orders",
        "preferred_cols": {
            "customer_col": ["customer_id", "user_id", "cust_id"],
        },
        "owner": "Marketing",
        "tags": ["customers", "kpi"],
    },
    {
        "keywords": ["profit", "gross profit"],
        "name": "Profit",
        "expression_template": "SUM({amount_col} - COALESCE({discount_col}, 0) - COALESCE({cost_col}, 0))",
        "description": "Estimated profit after discounts and cost",
        "preferred_cols": {
            "amount_col": ["gross_amount", "amount", "revenue"],
            "discount_col": ["discount", "discount_amount"],
            "cost_col": ["cost", "cogs", "unit_cost"],
        },
        "owner": "Finance",
        "tags": ["financial", "kpi"],
    },
    {
        "keywords": ["order count", "number of orders", "total orders"],
        "name": "Order Count",
        "expression_template": "COUNT(DISTINCT {order_col})",
        "description": "Total number of orders",
        "preferred_cols": {
            "order_col": ["order_id", "id"],
        },
        "owner": "Operations",
        "tags": ["orders", "volume"],
    },
    {
        "keywords": ["items sold", "quantity sold", "units sold"],
        "name": "Items Sold",
        "expression_template": "SUM({qty_col})",
        "description": "Total quantity of items sold",
        "preferred_cols": {
            "qty_col": ["quantity", "qty", "units"],
        },
        "owner": "Operations",
        "tags": ["operations", "volume"],
    },
    {
        "keywords": ["tax", "total tax", "tax collected"],
        "name": "Total Tax Collected",
        "expression_template": "SUM({tax_col})",
        "description": "Sum of tax amounts",
        "preferred_cols": {
            "tax_col": ["tax", "tax_amount", "vat"],
        },
        "owner": "Finance",
        "tags": ["financial", "tax"],
    },
]


def _find_column(schema: dict, candidates: list[str]) -> tuple[str, str] | None:
    """Return (table.column, table) for the first matching candidate column."""
    for table, meta in schema.items():
        cols = meta.get("columns", {})
        for cand in candidates:
            if cand in cols:
                return f"{table}.{cand}", table
            # fuzzy: ignore underscores
            for real in cols:
                if real.lower().replace("_", "") == cand.lower().replace("_", ""):
                    return f"{table}.{real}", table
    return None


def suggest_metric_from_nl(query: str, schema: dict) -> dict | None:
    """
    Convert a natural-language request into a structured metric suggestion.
    Example: "I need net revenue after discounts"
    """
    q = query.lower().strip()
    best = None
    best_score = 0

    for pattern in METRIC_PATTERNS:
        score = 0
        for kw in pattern["keywords"]:
            if kw in q:
                score += len(kw)
        if score > best_score:
            best_score = score
            best = pattern

    if not best or best_score == 0:
        return _generic_suggestion(query, schema)

    # Resolve columns from schema
    resolved = {}
    missing = []
    for placeholder, candidates in best["preferred_cols"].items():
        found = _find_column(schema, candidates)
        if found:
            resolved[placeholder] = found[0]
        else:
            missing.append(placeholder)

    if missing:
        # Still return a partial suggestion
        expr = best["expression_template"]
        for ph in missing:
            expr = expr.replace("{" + ph + "}", f"<{ph}>")
        for ph, col in resolved.items():
            expr = expr.replace("{" + ph + "}", col)
    else:
        expr = best["expression_template"]
        for ph, col in resolved.items():
            expr = expr.replace("{" + ph + "}", col)

    tables = list({c.split(".")[0] for c in resolved.values()})
    columns = list(resolved.values())

    return {
        "name": best["name"],
        "description": best["description"],
        "expression": expr,
        "tables": tables,
        "columns": columns,
        "owner": best.get("owner", "Analytics"),
        "tags": best.get("tags", []),
        "status": "draft",
        "ai_confidence": min(0.95, 0.5 + best_score / 20),
        "ai_note": f"Matched pattern for '{best['keywords'][0]}'. "
                   + (f"Could not auto-resolve: {missing}" if missing else "All columns resolved from schema."),
    }


def _generic_suggestion(query: str, schema: dict) -> dict | None:
    """Fallback when no strong pattern matches."""
    # Try to pick a numeric column and wrap with SUM
    for table, meta in schema.items():
        for col, info in meta.get("columns", {}).items():
            t = info.get("type", "").upper()
            if t in ("DECIMAL", "NUMERIC", "FLOAT", "DOUBLE", "INTEGER", "BIGINT"):
                if any(w in col.lower() for w in ["amount", "price", "total", "value", "revenue", "sales"]):
                    return {
                        "name": query.title()[:40] or "New Metric",
                        "description": f"AI-generated metric based on: {query}",
                        "expression": f"SUM({table}.{col})",
                        "tables": [table],
                        "columns": [f"{table}.{col}"],
                        "owner": "Analytics",
                        "tags": ["ai-suggested"],
                        "status": "draft",
                        "ai_confidence": 0.45,
                        "ai_note": "No strong pattern matched. Suggested SUM over a numeric amount-like column.",
                    }
    return {
        "name": "New Metric",
        "description": f"Please refine: {query}",
        "expression": "SUM(<table>.<column>)",
        "tables": [],
        "columns": [],
        "owner": "Analytics",
        "tags": ["ai-suggested"],
        "status": "draft",
        "ai_confidence": 0.2,
        "ai_note": "Could not confidently map the request to existing schema columns.",
    }


def suggest_metrics_for_schema(schema: dict) -> list[dict]:
    """Proactively suggest a set of useful metrics given a schema."""
    suggestions = []
    seen_names = set()
    for pattern in METRIC_PATTERNS:
        resolved = {}
        ok = True
        for placeholder, candidates in pattern["preferred_cols"].items():
            found = _find_column(schema, candidates)
            if found:
                resolved[placeholder] = found[0]
            else:
                # optional columns can be skipped for some patterns
                if "discount" in placeholder or "cost" in placeholder:
                    continue
                ok = False
                break
        if not ok or not resolved:
            continue

        expr = pattern["expression_template"]
        for ph, col in resolved.items():
            expr = expr.replace("{" + ph + "}", col)
        # clean unresolved optional placeholders
        expr = re.sub(r"COALESCE\([^)]*<[^>]+>[^)]*\)", "0", expr)
        expr = re.sub(r"\{[^}]+\}", "0", expr)

        name = pattern["name"]
        if name in seen_names:
            continue
        seen_names.add(name)

        suggestions.append({
            "name": name,
            "description": pattern["description"],
            "expression": expr,
            "tables": list({c.split(".")[0] for c in resolved.values()}),
            "columns": list(resolved.values()),
            "owner": pattern.get("owner", "Analytics"),
            "tags": pattern.get("tags", []) + ["ai-suggested"],
            "status": "draft",
            "ai_confidence": 0.8,
            "ai_note": "Auto-suggested from schema column analysis",
        })
    return suggestions


def explain_metric(metric: dict) -> str:
    """Generate a human-readable explanation of a metric definition."""
    name = metric.get("name", "Metric")
    expr = metric.get("expression", "")
    desc = metric.get("description", "")
    cols = metric.get("columns", [])
    owner = metric.get("owner", "—")

    lines = [
        f"**{name}**",
        f"Definition: {desc}" if desc else "",
        f"Formula: `{expr}`",
        f"Owner: {owner}",
        f"Depends on columns: {', '.join(cols) if cols else 'none detected'}",
    ]
    # Simple semantic explanation
    if "SUM(" in expr.upper() and "discount" in expr.lower():
        lines.append("This calculates a total after subtracting discounts — the recommended canonical Revenue definition.")
    elif "COUNT(DISTINCT" in expr.upper():
        lines.append("This counts unique entities (e.g. customers or orders), avoiding double-counting.")
    elif "AVG(" in expr.upper():
        lines.append("This computes an average value across the selected records.")

    return "\n".join(l for l in lines if l)


def detect_definition_conflicts(metrics: dict) -> list[dict]:
    """
    Find metrics that look like they measure the same concept but have different expressions.
    (Simple AI-ish consistency check.)
    """
    conflicts = []
    names = list(metrics.keys())
    for i, n1 in enumerate(names):
        m1 = metrics[n1]
        tags1 = set(t.lower() for t in m1.get("tags", []))
        for n2 in names[i + 1 :]:
            m2 = metrics[n2]
            tags2 = set(t.lower() for t in m2.get("tags", []))
            # Same concept heuristic
            similar_name = (
                n1.lower() in n2.lower()
                or n2.lower() in n1.lower()
                or len(tags1 & tags2) >= 2
            )
            if similar_name and m1.get("expression") != m2.get("expression"):
                conflicts.append({
                    "metric_a": n1,
                    "metric_b": n2,
                    "expression_a": m1.get("expression"),
                    "expression_b": m2.get("expression"),
                    "shared_tags": list(tags1 & tags2),
                    "recommendation": "Review both definitions and consolidate into one canonical metric.",
                })
    return conflicts
