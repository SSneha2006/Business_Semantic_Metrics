"""
Business Intelligence Semantic Layer
with Metric Definition Consistency — Professional Demo Application

Run:  streamlit run app/main.py
"""

from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from modules import schema_manager as sm
from modules import metric_manager as mm
from modules import ai_helper as ai

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Semantic BI Layer | Metric Consistency",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-header {
        font-size: 1.75rem; font-weight: 700; color: #0F172A;
        margin-bottom: 0.15rem; letter-spacing: -0.02em;
    }
    .sub-header { color: #64748B; font-size: 0.92rem; margin-bottom: 1.4rem; }
    .metric-card {
        background: #F8FAFC; border-left: 4px solid #2563EB;
        padding: 0.85rem 1.1rem; border-radius: 8px; margin-bottom: 0.55rem;
        border: 1px solid #E2E8F0;
    }
    .critical { border-left-color: #DC2626 !important; background: #FEF2F2; }
    .high { border-left-color: #EA580C !important; background: #FFF7ED; }
    .ok { border-left-color: #16A34A !important; background: #F0FDF4; }
    .kpi-box {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 1.1rem 1.2rem; text-align: center;
    }
    .kpi-value { font-size: 1.8rem; font-weight: 700; color: #1E40AF; }
    .kpi-label { font-size: 0.78rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em; }
    .section-card {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 1.2rem; margin-bottom: 1rem;
    }
    div[data-testid="stSidebar"] { background: #0F172A; }
    div[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        background: #F1F5F9; border-radius: 8px 8px 0 0;
        padding: 8px 18px; font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------
@st.cache_resource
def bootstrap():
    sm.seed_demo_schema()
    mm.seed_demo_metrics()
    return True

bootstrap()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.markdown("## 📊 Semantic BI Layer")
st.sidebar.caption("Metric Definition Consistency Platform")
page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🏗️ System Architecture",
        "📐 Schema Manager",
        "📏 Metric Catalog",
        "🤖 AI Metric Assistant",
        "⚡ Impact Analysis",
        "🔗 Lineage & Data Flow",
        "📈 Analytics & Reports",
        "ℹ️ About Project",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Project Team**")
st.sidebar.markdown("""
| Role | Reg. No |
|------|---------|
| Leader | 2300031380 |
| Member | 2300030498 |
| Member | 2300033824 |
| Member | 2300033757 |
""")
st.sidebar.caption("CSE-2 · KL University · Review-II")

# ===========================================================================
# HELPER: Architecture Diagram (Plotly)
# ===========================================================================
def render_architecture_diagram():
    fig = go.Figure()

    # Layer boxes as shapes
    layers = [
        {"y": 3.2, "label": "BI Tools Layer", "sub": "Power BI  ·  Tableau  ·  Looker  ·  Custom Dashboards", "color": "#DBEAFE"},
        {"y": 2.2, "label": "Semantic Layer (Core)", "sub": "Metric Catalog  ·  Business Rules  ·  Validation  ·  Consistency Engine", "color": "#D1FAE5"},
        {"y": 1.2, "label": "Governance & Intelligence", "sub": "Schema Registry  ·  Change Detection  ·  Impact Analysis  ·  AI Assistant  ·  Lineage", "color": "#FEF3C7"},
        {"y": 0.2, "label": "Data Sources", "sub": "PostgreSQL  ·  Data Warehouse  ·  Lakehouse  ·  Apache Spark", "color": "#FECACA"},
    ]

    for L in layers:
        fig.add_shape(type="rect", x0=0.5, x1=9.5, y0=L["y"], y1=L["y"] + 0.85,
                      fillcolor=L["color"], line=dict(color="#94A3B8", width=1.5), layer="below")
        fig.add_annotation(x=5, y=L["y"] + 0.58, text=f"<b>{L['label']}</b>",
                           showarrow=False, font=dict(size=14, color="#0F172A"))
        fig.add_annotation(x=5, y=L["y"] + 0.28, text=L["sub"],
                           showarrow=False, font=dict(size=11, color="#475569"))

    # Arrows between layers
    for y in [3.05, 2.05, 1.05]:
        fig.add_annotation(x=5, y=y, ax=5, ay=y - 0.15,
                           arrowhead=2, arrowsize=1.2, arrowwidth=1.5, arrowcolor="#64748B",
                           showarrow=True, text="")

    fig.update_layout(
        height=420, margin=dict(l=20, r=20, t=30, b=10),
        xaxis=dict(visible=False, range=[0, 10]),
        yaxis=dict(visible=False, range=[0, 4.2]),
        plot_bgcolor="white", paper_bgcolor="white",
        title=dict(text="System Architecture — Semantic BI Layer", font=dict(size=16, color="#0F172A")),
    )
    return fig


def render_dataflow_diagram():
    fig = go.Figure()

    steps = [
        (1, 2.5, "1. Collect\nData"),
        (2.5, 2.5, "2. Read\nSchema"),
        (4, 2.5, "3. Detect\nChanges"),
        (5.5, 2.5, "4. Define\nMetrics"),
        (7, 2.5, "5. Build\nSemantic Layer"),
        (2.5, 0.8, "6. Validate\nMetrics"),
        (4, 0.8, "7. Impact\nAnalysis"),
        (5.5, 0.8, "8. Track\nLineage"),
        (7, 0.8, "9. Serve to\nBI Tools"),
    ]
    colors = ["#3B82F6", "#3B82F6", "#F59E0B", "#10B981", "#10B981",
              "#8B5CF6", "#EF4444", "#6366F1", "#0EA5E9"]

    for i, (x, y, label) in enumerate(steps):
        fig.add_shape(type="rect", x0=x - 0.55, x1=x + 0.55, y0=y - 0.4, y1=y + 0.4,
                      fillcolor=colors[i], line=dict(color="white", width=2), layer="below")
        fig.add_annotation(x=x, y=y, text=f"<b>{label}</b>", showarrow=False,
                           font=dict(size=11, color="white"))

    # Top row arrows
    for x in [1.6, 3.1, 4.6, 6.1]:
        fig.add_annotation(x=x + 0.35, y=2.5, ax=x - 0.35, ay=2.5,
                           arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="#64748B")
    # Down from 5
    fig.add_annotation(x=7, y=1.35, ax=7, ay=2.05,
                       arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="#64748B")
    # Bottom row arrows
    for x in [3.1, 4.6, 6.1]:
        fig.add_annotation(x=x + 0.35, y=0.8, ax=x - 0.35, ay=0.8,
                           arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="#64748B")
    # Connect 3 down to 6
    fig.add_annotation(x=2.5, y=1.35, ax=2.5, ay=2.05,
                       arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="#64748B")

    fig.update_layout(
        height=340, margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(visible=False, range=[0.2, 7.8]),
        yaxis=dict(visible=False, range=[0.1, 3.2]),
        plot_bgcolor="white", paper_bgcolor="white",
        title=dict(text="End-to-End Data & Metric Workflow", font=dict(size=15, color="#0F172A")),
    )
    return fig


def render_schema_er_diagram(schema: dict):
    """Simple ER-style view of tables and key relationships."""
    fig = go.Figure()
    tables = list(schema.keys())
    positions = {
        "orders": (2, 2.2),
        "customers": (0.5, 0.8),
        "order_items": (3.5, 0.8),
        "products": (5.5, 0.8),
        "returns": (2, 0.2),
    }
    # default positions for any extra tables
    for i, t in enumerate(tables):
        if t not in positions:
            positions[t] = (1 + i * 1.5, 3.0)

    for tname in tables:
        x, y = positions.get(tname, (2, 2))
        cols = list(schema[tname].get("columns", {}).keys())[:6]
        col_text = "<br>".join(f"• {c}" for c in cols)
        if len(schema[tname].get("columns", {})) > 6:
            col_text += "<br>• …"
        fig.add_shape(type="rect", x0=x - 0.7, x1=x + 0.7, y0=y - 0.55, y1=y + 0.55,
                      fillcolor="#EFF6FF", line=dict(color="#2563EB", width=2))
        fig.add_annotation(x=x, y=y + 0.38, text=f"<b>{tname}</b>", showarrow=False,
                           font=dict(size=12, color="#1E40AF"))
        fig.add_annotation(x=x, y=y - 0.05, text=col_text, showarrow=False,
                           font=dict(size=9, color="#334155"), align="left")

    # Relationship lines (orders-centric)
    rels = [
        ("customers", "orders"),
        ("orders", "order_items"),
        ("products", "order_items"),
    ]
    for a, b in rels:
        if a in positions and b in positions:
            xa, ya = positions[a]
            xb, yb = positions[b]
            fig.add_annotation(x=xb, y=yb, ax=xa, ay=ya,
                               arrowhead=2, arrowsize=1, arrowwidth=1.2, arrowcolor="#94A3B8")

    fig.update_layout(
        height=380, margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(visible=False, range=[-0.5, 6.5]),
        yaxis=dict(visible=False, range=[-0.5, 3.2]),
        plot_bgcolor="white", paper_bgcolor="white",
        title=dict(text="Schema ER Overview (Demo E-Commerce)", font=dict(size=15, color="#0F172A")),
    )
    return fig


def render_lineage_graph(lineage: dict):
    nodes = lineage.get("nodes", [])
    col_nodes = [n for n in nodes if n["type"] == "column"]
    table_nodes = [n for n in nodes if n["type"] == "table"]
    metric_nodes = [n for n in nodes if n["type"] == "metric"]

    fig = go.Figure()

    def ypos(group, i):
        n = len(group)
        return 0.5 if n == 1 else i / max(n - 1, 1)

    for i, n in enumerate(col_nodes):
        fig.add_trace(go.Scatter(
            x=[0], y=[ypos(col_nodes, i)], mode="markers+text",
            marker=dict(size=26, color="#3B82F6", line=dict(width=1, color="white")),
            text=[n["label"].split(".")[-1]], textposition="middle left",
            name="Column", showlegend=(i == 0),
            hovertext=n["label"], hoverinfo="text",
        ))
    for i, n in enumerate(table_nodes):
        fig.add_trace(go.Scatter(
            x=[1], y=[ypos(table_nodes, i)], mode="markers+text",
            marker=dict(size=34, color="#10B981", line=dict(width=1, color="white")),
            text=[n["label"]], textposition="top center",
            name="Table", showlegend=(i == 0),
        ))
    for i, n in enumerate(metric_nodes):
        fig.add_trace(go.Scatter(
            x=[2], y=[0.5], mode="markers+text",
            marker=dict(size=46, color="#F59E0B", line=dict(width=2, color="white")),
            text=[n["label"]], textposition="middle right",
            name="Metric", showlegend=(i == 0),
        ))

    # Connecting lines
    for cn in col_nodes:
        for tn in table_nodes:
            if cn["label"].startswith(tn["label"] + "."):
                fig.add_shape(type="line", x0=0, x1=1,
                              y0=ypos(col_nodes, col_nodes.index(cn)),
                              y1=ypos(table_nodes, table_nodes.index(tn)),
                              line=dict(color="#CBD5E1", width=1.5))
        for mn in metric_nodes:
            fig.add_shape(type="line", x0=0, x1=2,
                          y0=ypos(col_nodes, col_nodes.index(cn)), y1=0.5,
                          line=dict(color="#E2E8F0", width=1, dash="dot"))
    for tn in table_nodes:
        for mn in metric_nodes:
            fig.add_shape(type="line", x0=1, x1=2,
                          y0=ypos(table_nodes, table_nodes.index(tn)), y1=0.5,
                          line=dict(color="#94A3B8", width=2))

    fig.update_layout(
        height=300, margin=dict(l=80, r=100, t=40, b=20),
        xaxis=dict(visible=False, range=[-0.4, 2.5]),
        yaxis=dict(visible=False, range=[-0.15, 1.15]),
        plot_bgcolor="white", paper_bgcolor="white",
        title=dict(text=f"Lineage: {lineage.get('metric', '')}", font=dict(size=14)),
        legend=dict(orientation="h", y=1.12),
    )
    return fig


# ===========================================================================
# PAGE: Dashboard
# ===========================================================================
if page == "🏠 Dashboard":
    st.markdown('<p class="main-header">Semantic Layer Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Single source of truth for business metrics · Consistency · Governance · Traceability</p>', unsafe_allow_html=True)

    metrics = mm.get_all_metrics()
    schema = sm.get_current_schema("demo_ecommerce")
    changes = sm.get_change_log(limit=20)
    conflicts = ai.detect_definition_conflicts(metrics)

    # KPI row
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f'<div class="kpi-box"><div class="kpi-value">{len(metrics)}</div><div class="kpi-label">Metrics</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-box"><div class="kpi-value">{len(schema)}</div><div class="kpi-label">Tables</div></div>', unsafe_allow_html=True)
    with k3:
        total_cols = sum(len(t.get("columns", {})) for t in schema.values())
        st.markdown(f'<div class="kpi-box"><div class="kpi-value">{total_cols}</div><div class="kpi-label">Columns</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-box"><div class="kpi-value">{len(changes)}</div><div class="kpi-label">Schema Events</div></div>', unsafe_allow_html=True)
    with k5:
        conf_color = "#16A34A" if not conflicts else "#DC2626"
        st.markdown(f'<div class="kpi-box"><div class="kpi-value" style="color:{conf_color}">{len(conflicts)}</div><div class="kpi-label">Conflicts</div></div>', unsafe_allow_html=True)

    st.markdown("")
    col_l, col_r = st.columns([1.3, 1])

    with col_l:
        st.subheader("Active Metric Catalog")
        if not metrics:
            st.info("No metrics defined. Use Metric Catalog or AI Assistant.")
        else:
            for name, m in list(metrics.items())[:8]:
                status = m.get("status", "active")
                badge = {"active": "🟢", "draft": "🟡", "deprecated": "🔴"}.get(status, "⚪")
                st.markdown(
                    f"""<div class="metric-card">
                    <b>{badge} {name}</b> &nbsp; <code style="font-size:0.78rem;background:#F1F5F9;padding:2px 6px;border-radius:4px;">{m.get('expression','')}</code><br>
                    <small style="color:#64748B;">{m.get('description','')} · Owner: <b>{m.get('owner','—')}</b> · v{m.get('version',1)}</small>
                    </div>""",
                    unsafe_allow_html=True,
                )

    with col_r:
        st.subheader("Consistency Status")
        if not conflicts:
            st.success("✅ All metric definitions are consistent. No conflicts detected.")
        else:
            st.warning(f"⚠ {len(conflicts)} potential definition conflict(s)")
            for c in conflicts:
                st.markdown(f"**{c['metric_a']}** vs **{c['metric_b']}**")
                st.caption(c.get("recommendation", ""))

        st.markdown("---")
        st.subheader("Latest Schema Events")
        if not changes:
            st.info("No schema changes yet. Try Schema Manager → Simulate Change.")
        else:
            for entry in changes[:4]:
                st.caption(f"**{entry['timestamp'][:19]}** · `{entry['source']}`")
                for ch in entry.get("changes", [])[:2]:
                    icon = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(ch.get("severity"), "⚪")
                    st.markdown(f"{icon} {ch['detail']}")

    # Mini architecture preview
    st.markdown("---")
    st.subheader("Platform Architecture (Overview)")
    st.plotly_chart(render_architecture_diagram(), use_container_width=True)

# ===========================================================================
# PAGE: System Architecture
# ===========================================================================
elif page == "🏗️ System Architecture":
    st.markdown('<p class="main-header">System Architecture & Design</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Layered design ensuring metric consistency, schema governance and AI-assisted definition</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Architecture Diagram", "Data Flow Workflow", "Module Mapping"])

    with tab1:
        st.plotly_chart(render_architecture_diagram(), use_container_width=True)
        st.markdown("""
        **Layer responsibilities**
        | Layer | Responsibility |
        |-------|----------------|
        | **BI Tools** | Consume consistent metrics for reports & dashboards |
        | **Semantic Layer** | Single catalog of metric definitions, validation, business rules |
        | **Governance & Intelligence** | Schema registry, change detection, impact analysis, AI, lineage |
        | **Data Sources** | Operational DBs, warehouse, lakehouse, processing engines |
        """)

    with tab2:
        st.plotly_chart(render_dataflow_diagram(), use_container_width=True)
        st.markdown("""
        **Workflow summary**
        1. Connect & collect metadata from data sources  
        2. Persist schema snapshot  
        3. Detect structural changes (add / remove / rename / modify)  
        4. Define metrics once in the semantic catalog  
        5. Bind metrics to columns & enforce consistency  
        6. Validate expressions against live schema  
        7. Run impact analysis on every change  
        8. Maintain full column → table → metric lineage  
        9. Serve the same definition to every BI tool  
        """)

    with tab3:
        st.markdown("#### Project Modules ↔ Implementation")
        mapping = pd.DataFrame([
            ["Data Source Module", "schema_manager.py", "Connect & read source schemas"],
            ["Schema Management", "schema_manager.py", "Store schemas, detect changes"],
            ["Metric Management", "metric_manager.py", "CRUD metrics, versioning"],
            ["Semantic Layer", "metric_manager.py + main UI", "Central consistent definitions"],
            ["Validation Module", "metric_manager.validate_metric()", "Expression & schema checks"],
            ["Impact Analysis", "metric_manager.impact_analysis()", "Find affected metrics"],
            ["Lineage Module", "metric_manager.get_lineage()", "Column → Table → Metric graph"],
            ["AI Assistant", "ai_helper.py", "NL→metric, suggestions, conflicts"],
            ["User Interface", "app/main.py (Streamlit)", "All interactive pages"],
        ], columns=["Project Module", "Code Location", "Function"])
        st.dataframe(mapping, use_container_width=True, hide_index=True)

        st.markdown("#### Technology Stack")
        tech = pd.DataFrame([
            ["Python 3.12", "Core logic & automation"],
            ["Streamlit", "Interactive professional UI"],
            ["Pandas / Plotly", "Data handling & diagrams"],
            ["JSON store (demo)", "Persistence (swap for PostgreSQL in production)"],
            ["Rule-based AI engine", "Metric suggestion & conflict detection"],
            ["Docker-ready", "Deployment (production extension)"],
        ], columns=["Technology", "Role"])
        st.dataframe(tech, use_container_width=True, hide_index=True)

# ===========================================================================
# PAGE: Schema Manager
# ===========================================================================
elif page == "📐 Schema Manager":
    st.markdown('<p class="main-header">Schema Manager</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Schema registry · Change detection · Evolution simulation</p>', unsafe_allow_html=True)

    schema = sm.get_current_schema("demo_ecommerce")
    if not schema:
        sm.seed_demo_schema()
        schema = sm.get_current_schema("demo_ecommerce")

    tab1, tab2, tab3, tab4 = st.tabs(["Current Schema", "ER Diagram", "Simulate Change", "Change Audit Log"])

    with tab1:
        for tname, tmeta in schema.items():
            with st.expander(f"📁 **{tname}**  ·  {len(tmeta.get('columns', {}))} columns", expanded=(tname == "orders")):
                rows = [{"Column": c, "Type": m.get("type", ""), "Nullable": m.get("nullable", True)}
                        for c, m in tmeta.get("columns", {}).items()]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with tab2:
        st.plotly_chart(render_schema_er_diagram(schema), use_container_width=True)
        st.caption("Entity-Relationship style overview of the demo e-commerce schema used for metric definitions.")

    with tab3:
        st.markdown("#### Simulate real-world schema evolution")
        st.info("These scenarios demonstrate automatic detection of ADDED / REMOVED / RENAMED / MODIFIED columns and tables.")
        variant = st.selectbox(
            "Change scenario",
            [
                ("rename_discount", "Rename column: discount → discount_amount"),
                ("remove_tax", "Remove column: tax"),
                ("add_shipping", "Add column: shipping_cost"),
                ("change_type", "Modify type: order_items.quantity INTEGER → BIGINT"),
                ("add_table", "Add new table: returns"),
            ],
            format_func=lambda x: x[1],
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶ Apply Change & Detect", type="primary", use_container_width=True):
                changes = sm.apply_demo_schema_change(variant[0])
                if changes:
                    st.success(f"Detected **{len(changes)}** change(s)")
                    for ch in changes:
                        sev = ch.get("severity", "medium")
                        cls = "critical" if sev == "critical" else ("high" if sev == "high" else "ok")
                        st.markdown(f'<div class="metric-card {cls}"><b>{ch["type"]}</b> — {ch["detail"]}</div>', unsafe_allow_html=True)
                    impacted = mm.impact_analysis(changes)
                    if impacted:
                        st.markdown("#### ⚡ Metrics Impacted")
                        for imp in impacted:
                            st.error(f"**{imp['metric']}** ({imp['severity']}) — {'; '.join(imp['reasons'])}")
                    else:
                        st.info("No defined metrics were affected.")
                else:
                    st.info("No differences detected (schema may already be in this state). Try another scenario or reset.")
        with c2:
            if st.button("↺ Reset Demo Schema", use_container_width=True):
                from modules.schema_manager import SCHEMA_FILE
                if SCHEMA_FILE.exists():
                    SCHEMA_FILE.unlink()
                sm.seed_demo_schema()
                st.success("Schema reset to original demo state.")
                st.rerun()

    with tab4:
        log = sm.get_change_log(limit=40)
        if not log:
            st.info("No changes logged yet. Run a simulation above.")
        else:
            for entry in log:
                with st.expander(f"{entry['timestamp'][:19]} UTC  ·  {entry['source']}  ·  {len(entry.get('changes',[]))} change(s)"):
                    for ch in entry.get("changes", []):
                        st.markdown(f"- **[{ch['type']}]** {ch['detail']}  · severity: `{ch.get('severity')}`")

# ===========================================================================
# PAGE: Metric Catalog
# ===========================================================================
elif page == "📏 Metric Catalog":
    st.markdown('<p class="main-header">Metric Catalog (Semantic Layer)</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">One canonical definition per business metric — the core of consistency</p>', unsafe_allow_html=True)

    metrics = mm.get_all_metrics()
    schema = sm.get_current_schema("demo_ecommerce")

    tab1, tab2, tab3 = st.tabs(["Browse Metrics", "Create / Edit Metric", "Validate All"])

    with tab1:
        if not metrics:
            st.info("No metrics yet. Create one or use the AI Assistant.")
        else:
            # Summary table
            summary = []
            for name, m in metrics.items():
                summary.append({
                    "Metric": name,
                    "Owner": m.get("owner", "—"),
                    "Status": m.get("status", "active"),
                    "Version": m.get("version", 1),
                    "Columns": len(m.get("columns", [])),
                    "Tags": ", ".join(m.get("tags", [])),
                })
            st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

            st.markdown("---")
            for name, m in metrics.items():
                with st.expander(f"{'🟢' if m.get('status')=='active' else '🟡'} **{name}** — {m.get('owner','')}", expanded=False):
                    st.markdown(f"**Description:** {m.get('description','')}")
                    st.code(m.get("expression", ""), language="sql")
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Tables:** {', '.join(m.get('tables', []))}")
                    c2.write(f"**Version:** {m.get('version', 1)}")
                    c3.write(f"**Tags:** {', '.join(m.get('tags', []))}")
                    st.caption(f"Updated: {m.get('updated_at', '')[:19]}")
                    if st.button(f"Delete '{name}'", key=f"del_{name}"):
                        mm.delete_metric(name)
                        st.rerun()

    with tab2:
        st.markdown("#### Define a new metric (or overwrite by name)")
        with st.form("metric_form"):
            name = st.text_input("Metric Name *", placeholder="e.g. Revenue")
            description = st.text_area("Business Description", placeholder="Clear business meaning")
            expression = st.text_area("Expression (SQL-like) *",
                                      placeholder="SUM(orders.gross_amount - COALESCE(orders.discount, 0))", height=80)
            owner = st.text_input("Owner / Team", value="Analytics")
            tags = st.text_input("Tags (comma-separated)", value="kpi")
            status = st.selectbox("Status", ["active", "draft", "deprecated"])
            submitted = st.form_submit_button("💾 Save Metric", type="primary")

            if submitted:
                if not name or not expression:
                    st.error("Name and Expression are required.")
                else:
                    metric = {
                        "name": name, "description": description, "expression": expression,
                        "owner": owner, "tags": [t.strip() for t in tags.split(",") if t.strip()],
                        "status": status,
                    }
                    result = mm.validate_metric(metric, schema)
                    if result["valid"]:
                        metric["columns"] = result["referenced_columns"]
                        metric["tables"] = result["referenced_tables"]
                        mm.save_metric(metric)
                        st.success(f"Metric **{name}** saved to the semantic catalog.")
                        for w in result.get("warnings", []):
                            st.warning(w)
                    else:
                        st.error("Validation failed:")
                        for e in result["errors"]:
                            st.write(f"• {e}")

    with tab3:
        st.markdown("#### Validate every metric against the current schema")
        if st.button("Run Full Validation", type="primary"):
            rows = []
            for name, m in metrics.items():
                res = mm.validate_metric(m, schema)
                rows.append({
                    "Metric": name,
                    "Valid": "✅ Yes" if res["valid"] else "❌ No",
                    "Errors": "; ".join(res["errors"]) or "—",
                    "Warnings": "; ".join(res["warnings"]) or "—",
                })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info("No metrics to validate.")

# ===========================================================================
# PAGE: AI Metric Assistant
# ===========================================================================
elif page == "🤖 AI Metric Assistant":
    st.markdown('<p class="main-header">AI Metric Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Natural language → consistent metric definitions aligned to your schema</p>', unsafe_allow_html=True)

    schema = sm.get_current_schema("demo_ecommerce")

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("#### Natural Language → Metric")
        query = st.text_input("Describe the metric you need",
                              placeholder="e.g. net revenue after discounts, average order value, unique customers")
        if st.button("✨ Generate Suggestion", type="primary") and query:
            suggestion = ai.suggest_metric_from_nl(query, schema)
            if suggestion:
                st.session_state["ai_suggestion"] = suggestion

        if "ai_suggestion" in st.session_state:
            s = st.session_state["ai_suggestion"]
            conf = s.get("ai_confidence", 0)
            st.markdown(f"**Suggested: {s['name']}**  · Confidence: **{conf:.0%}**")
            st.info(s.get("ai_note", ""))
            st.code(s.get("expression", ""), language="sql")
            st.write(s.get("description", ""))
            if st.button("💾 Accept & Save to Catalog", type="primary"):
                s["status"] = "active"
                mm.save_metric(s)
                st.success(f"Saved **{s['name']}** to the metric catalog.")
                del st.session_state["ai_suggestion"]
                st.rerun()

    with col2:
        st.markdown("#### Auto-suggest from Schema")
        st.caption("AI scans columns and proposes standard business KPIs.")
        if st.button("🔍 Analyse Schema & Suggest"):
            st.session_state["schema_suggestions"] = ai.suggest_metrics_for_schema(schema)

        if "schema_suggestions" in st.session_state:
            for s in st.session_state["schema_suggestions"]:
                already = mm.get_metric(s["name"]) is not None
                with st.expander(f"{'✓ Already exists — ' if already else ''}{s['name']}", expanded=False):
                    st.code(s["expression"], language="sql")
                    st.caption(s.get("ai_note", ""))
                    if not already and st.button(f"Add {s['name']}", key=f"add_{s['name']}"):
                        mm.save_metric(s)
                        st.success(f"Added {s['name']}")
                        st.rerun()

    st.markdown("---")
    st.markdown("#### Explain an Existing Metric")
    metrics = mm.get_all_metrics()
    if metrics:
        chosen = st.selectbox("Select metric to explain", list(metrics.keys()))
        if chosen:
            st.markdown(ai.explain_metric(metrics[chosen]))

# ===========================================================================
# PAGE: Impact Analysis
# ===========================================================================
elif page == "⚡ Impact Analysis":
    st.markdown('<p class="main-header">Impact Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Which metrics break when the database schema changes?</p>', unsafe_allow_html=True)

    log = sm.get_change_log(limit=20)
    if not log:
        st.warning("No schema changes recorded yet. Go to **Schema Manager → Simulate Change** first.")
    else:
        latest = log[0]
        st.markdown(f"**Latest change set** — `{latest['timestamp'][:19]} UTC`")
        for ch in latest.get("changes", []):
            st.caption(f"• [{ch['type']}] {ch['detail']}")

        impacted = mm.impact_analysis(latest.get("changes", []))
        st.markdown("---")
        if not impacted:
            st.success("✅ No metrics are affected by the latest schema changes.")
        else:
            st.error(f"**{len(impacted)} metric(s) impacted**")
            # Severity chart
            sev_counts = pd.DataFrame(impacted).groupby("severity").size().reset_index(name="count")
            if not sev_counts.empty:
                fig = px.bar(sev_counts, x="severity", y="count", color="severity",
                             color_discrete_map={"critical": "#DC2626", "high": "#EA580C", "medium": "#F59E0B", "low": "#64748B"},
                             title="Impact by Severity")
                fig.update_layout(height=260, margin=dict(t=40, b=20), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            for imp in impacted:
                sev = imp["severity"]
                cls = "critical" if sev == "critical" else "high"
                st.markdown(
                    f"""<div class="metric-card {cls}">
                    <b>{imp['metric']}</b> &nbsp; <span style="color:#DC2626;font-weight:600;">{sev.upper()}</span><br>
                    {'; '.join(imp['reasons'])}<br>
                    <code style="font-size:0.78rem;">{imp.get('expression','')}</code>
                    · Owner: {imp.get('owner','—')}
                    </div>""",
                    unsafe_allow_html=True,
                )

        st.markdown("#### Re-analyse a previous change set")
        options = [f"{e['timestamp'][:19]} ({len(e.get('changes',[]))} changes)" for e in log]
        idx = st.selectbox("Change set", range(len(options)), format_func=lambda i: options[i])
        if st.button("Re-run Impact Analysis"):
            selected = log[idx].get("changes", [])
            impacted2 = mm.impact_analysis(selected)
            if impacted2:
                for imp in impacted2:
                    st.warning(f"{imp['metric']} ({imp['severity']}): {'; '.join(imp['reasons'])}")
            else:
                st.success("No metrics affected.")

# ===========================================================================
# PAGE: Lineage & Data Flow
# ===========================================================================
elif page == "🔗 Lineage & Data Flow":
    st.markdown('<p class="main-header">Lineage Explorer & Data Flow</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Trace every metric back to the columns and tables it depends on</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Metric Lineage", "System Data Flow"])

    with tab1:
        metrics = mm.get_all_metrics()
        if not metrics:
            st.info("Define some metrics first.")
        else:
            chosen = st.selectbox("Select a metric", list(metrics.keys()))
            lineage = mm.get_lineage(chosen)
            if lineage:
                st.markdown(f"**Expression:** `{lineage['expression']}`")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### Tables")
                    for t in lineage.get("tables", []):
                        st.markdown(f"- 📁 `{t}`")
                with c2:
                    st.markdown("#### Columns")
                    for c in lineage.get("columns", []):
                        st.markdown(f"- 📎 `{c}`")
                st.plotly_chart(render_lineage_graph(lineage), use_container_width=True)
                st.caption("Any schema change on the left-side columns can break or alter the metric on the right.")

    with tab2:
        st.plotly_chart(render_dataflow_diagram(), use_container_width=True)
        st.markdown("""
        This workflow is implemented across the modules:
        - **Steps 1–3** → `schema_manager.py`
        - **Steps 4–5** → `metric_manager.py` (Semantic Layer)
        - **Step 6** → `validate_metric()`
        - **Step 7** → `impact_analysis()`
        - **Step 8** → `get_lineage()`
        - **Step 9** → exposed consistently to any BI client
        """)

# ===========================================================================
# PAGE: Analytics & Reports
# ===========================================================================
elif page == "📈 Analytics & Reports":
    st.markdown('<p class="main-header">Analytics & Governance Reports</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Metric coverage, ownership distribution and schema health</p>', unsafe_allow_html=True)

    metrics = mm.get_all_metrics()
    schema = sm.get_current_schema("demo_ecommerce")
    changes = sm.get_change_log(limit=50)

    if not metrics:
        st.info("No metrics yet.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            # Ownership distribution
            owners = {}
            for m in metrics.values():
                o = m.get("owner", "Unknown")
                owners[o] = owners.get(o, 0) + 1
            fig = px.pie(names=list(owners.keys()), values=list(owners.values()),
                         title="Metrics by Owner / Team", hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=320, margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Status distribution
            statuses = {}
            for m in metrics.values():
                s = m.get("status", "active")
                statuses[s] = statuses.get(s, 0) + 1
            fig2 = px.bar(x=list(statuses.keys()), y=list(statuses.values()),
                          title="Metrics by Status",
                          color=list(statuses.keys()),
                          color_discrete_map={"active": "#16A34A", "draft": "#F59E0B", "deprecated": "#DC2626"})
            fig2.update_layout(height=320, margin=dict(t=40, b=20), showlegend=False,
                               xaxis_title="", yaxis_title="Count")
            st.plotly_chart(fig2, use_container_width=True)

        # Tag cloud style table
        st.subheader("Metric Inventory")
        inv = []
        for name, m in metrics.items():
            inv.append({
                "Metric": name,
                "Expression": m.get("expression", "")[:55] + ("…" if len(m.get("expression", "")) > 55 else ""),
                "Owner": m.get("owner", "—"),
                "Status": m.get("status", "active"),
                "Version": m.get("version", 1),
                "Deps (cols)": len(m.get("columns", [])),
            })
        st.dataframe(pd.DataFrame(inv), use_container_width=True, hide_index=True)

        # Schema health
        st.subheader("Schema Health")
        h1, h2, h3 = st.columns(3)
        h1.metric("Tables tracked", len(schema))
        h2.metric("Total columns", sum(len(t.get("columns", {})) for t in schema.values()))
        h3.metric("Change events logged", len(changes))

        if changes:
            # Change type distribution
            all_types = []
            for e in changes:
                for ch in e.get("changes", []):
                    all_types.append(ch.get("type", "OTHER"))
            if all_types:
                tc = pd.Series(all_types).value_counts().reset_index()
                tc.columns = ["Change Type", "Count"]
                fig3 = px.bar(tc, x="Change Type", y="Count", title="Schema Change Types (Audit)",
                              color="Change Type", color_discrete_sequence=px.colors.qualitative.Pastel)
                fig3.update_layout(height=300, margin=dict(t=40, b=20), showlegend=False)
                st.plotly_chart(fig3, use_container_width=True)

# ===========================================================================
# PAGE: About
# ===========================================================================
elif page == "ℹ️ About Project":
    st.markdown('<p class="main-header">About This Project</p>', unsafe_allow_html=True)

    st.markdown("""
    ### Business Intelligence Semantic Layers with Metric Definition Consistency

    **Problem**  
    Different teams and BI tools define the same business metric (e.g. *Revenue*) differently.  
    Schema changes silently break reports. There is no single source of truth.

    **Solution**  
    A centralized **Semantic Layer** that:
    - Stores **one canonical definition** per metric  
    - Detects database schema changes automatically  
    - Runs **impact analysis** to show which metrics are affected  
    - Validates metric definitions before use  
    - Tracks full **lineage** (column → table → metric)  
    - Uses **AI** to help create consistent definitions from natural language  

    ---
    #### Modules implemented
    """)
    mods = pd.DataFrame([
        ["Schema Manager", "Store schemas + detect add/remove/rename/modify"],
        ["Metric Catalog", "CRUD, versioning, single source of truth"],
        ["Validation", "Expression & schema compatibility checks"],
        ["Impact Analysis", "Map schema changes → affected metrics"],
        ["Lineage", "Column → Table → Metric dependency graph"],
        ["AI Assistant", "NL→metric, auto-suggest, conflict detection"],
        ["Analytics", "Ownership, status, change-type reports"],
        ["UI", "Professional Streamlit multi-page application"],
    ], columns=["Module", "Capability"])
    st.dataframe(mods, use_container_width=True, hide_index=True)

    st.markdown("""
    #### Tech stack (demo)
    Python · Streamlit · Pandas · Plotly · JSON persistence  
    *(Production path: PostgreSQL, Apache Spark, Docker, real LLM APIs, BI connectors)*

    ---
    **Team**  
    Leader: **2300031380** · Members: **2300030498** · **2300033824** · **2300033757**  

    Department of Computer Science & Engineering-2  
    **KL University** · Review-II · 2026
    """)

    st.plotly_chart(render_architecture_diagram(), use_container_width=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption("Semantic BI Layer · Metric Definition Consistency · CSE-2 · KL University · Review-II 2026")
