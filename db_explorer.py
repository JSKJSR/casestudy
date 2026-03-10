"""
Intersport · Data Model Explorer
DB-style raw data viewer with schema, ERD, and FK relationships
Run: streamlit run db_explorer.py
"""
import warnings
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Intersport · Data Model Explorer",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    font-family: "Segoe UI", system-ui, sans-serif;
    background: #0f1117;
    color: #e0e6ef;
}
.block-container { padding: 1rem 1.5rem; max-width: 100%; background: #0f1117; }
section[data-testid="stSidebar"] > div:first-child { background: #141820 !important; border-right: 1px solid #2a3040; }
section[data-testid="stSidebar"] * { color: #e0e6ef !important; }
/* Table styling */
.db-table { width: 100%; border-collapse: collapse; font-size: 12px; font-family: "Segoe UI", monospace; }
.db-table thead tr { background: #141820; position: sticky; top: 0; }
.db-table thead th { padding: 8px 12px; text-align: left; border-bottom: 2px solid #2a3040; color: #6b7a99; font-size: 11px; font-weight: 700; letter-spacing: .5px; white-space: nowrap; }
.db-table tbody tr { border-bottom: 1px solid #1e2535; }
.db-table tbody tr:hover { background: #1a2238; }
.db-table tbody td { padding: 6px 12px; white-space: nowrap; max-width: 200px; overflow: hidden; text-overflow: ellipsis; }
.td-pk  { color: #fbbf24; font-family: monospace; font-size: 11px; }
.td-fk  { color: #a78bfa; font-family: monospace; font-size: 11px; }
.td-dt  { color: #34d399; font-family: monospace; font-size: 11px; }
.td-num { color: #38bdf8; font-family: monospace; font-size: 11px; text-align: right; }
.td-txt { color: #c9d4e8; }
/* Schema cards */
.schema-card { background: #1a2030; border: 1px solid #2a3040; border-radius: 8px; padding: 0; margin-bottom: 12px; overflow: hidden; }
.schema-card-hdr { padding: 8px 14px; font-size: 12px; font-weight: 700; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #2a3040; }
.schema-col-row { display: flex; padding: 4px 14px; border-bottom: 1px solid #1a1f2e; font-size: 11px; align-items: center; gap: 6px; }
.schema-col-row:last-child { border-bottom: none; }
.badge-pk  { background: #3a2e00; color: #fbbf24; font-size: 9px; font-weight: 700; padding: 1px 5px; border-radius: 3px; }
.badge-fk  { background: #2e1a4a; color: #a78bfa; font-size: 9px; font-weight: 700; padding: 1px 5px; border-radius: 3px; }
.badge-type{ color: #4a5568; font-size: 9px; font-family: monospace; margin-left: auto; }
/* Relationship pills */
.rel-row { display: flex; align-items: center; gap: 10px; padding: 8px 14px; background: #1a2030; border: 1px solid #2a3040; border-radius: 6px; margin-bottom: 8px; font-size: 12px; }
.rel-from { color: #60a5fa; font-weight: 700; }
.rel-col  { color: #a78bfa; font-family: monospace; font-size: 11px; }
.rel-to   { color: #4ade80; font-weight: 700; }
.rel-card { margin-left: auto; font-size: 10px; color: #fb923c; background: #1e2535; padding: 2px 8px; border-radius: 8px; }
div[data-testid="stMetricValue"] { color: #60a5fa !important; font-size: 20px !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
DATA_PATH = "data/"
EXCEL_PATH = "TDC - DS - Data Model Sales - Candidate.xlsx"

PK_MAP = {
    "Sales Orders": "Order ID",
    "Budget": None,
    "Store": "Store ID",
    "Product": "Product ID",
    "Customer": "Customer ID",
}
FK_MAP = {
    "Sales Orders": {"Store ID": "Store", "Product ID": "Product", "Customer ID": "Customer"},
    "Budget": {"Store ID": "Store"},
}
TABLE_META = {
    "Sales Orders": {"icon": "SO", "color": "#1e3a5f", "accent": "#60a5fa", "type": "FACT", "rows": "42,934"},
    "Budget":       {"icon": "BG", "color": "#3a1e1e", "accent": "#f87171", "type": "FACT", "rows": "8,107"},
    "Store":        {"icon": "ST", "color": "#1a3a2a", "accent": "#4ade80", "type": "DIM",  "rows": "27"},
    "Product":      {"icon": "PR", "color": "#3a2a1a", "accent": "#fb923c", "type": "DIM",  "rows": "3,789"},
    "Customer":     {"icon": "CU", "color": "#2a1a3a", "accent": "#c084fc", "type": "DIM",  "rows": "17,415"},
}

# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_all():
    try:
        tables = {
            "Sales Orders": pd.read_parquet(DATA_PATH + "sales.parquet"),
            "Budget":        pd.read_parquet(DATA_PATH + "budget.parquet"),
            "Store":         pd.read_parquet(DATA_PATH + "store.parquet"),
            "Product":       pd.read_parquet(DATA_PATH + "product.parquet"),
            "Customer":      pd.read_parquet(DATA_PATH + "customer.parquet"),
        }
    except Exception:
        xl = pd.ExcelFile(EXCEL_PATH)
        tables = {s: xl.parse(s) for s in xl.sheet_names}
    return tables

tables = load_all()

def col_type(df, col):
    dtype = str(df[col].dtype)
    if "datetime" in dtype: return "DATE"
    if "int" in dtype:      return "INT"
    if "float" in dtype:    return "FLOAT"
    return "TEXT"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⬡ Data Model Explorer")
    st.markdown("---")
    view = st.radio(
        "View",
        ["📐 Schema & ERD", "📋 Sales Orders", "💰 Budget", "🏪 Store", "📦 Product", "👤 Customer"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        "<div style='font-size:11px;color:#4a5568'>"
        "5 tables · 72,272 rows<br>Star Schema · 4 FK joins"
        "</div>",
        unsafe_allow_html=True,
    )

LABEL_MAP = {
    "📋 Sales Orders": "Sales Orders",
    "💰 Budget": "Budget",
    "🏪 Store": "Store",
    "📦 Product": "Product",
    "👤 Customer": "Customer",
}

# ── Helper: render styled HTML table ─────────────────────────────────────────
def render_table(name, df, search=""):
    pk   = PK_MAP.get(name)
    fks  = FK_MAP.get(name, {})
    cols = list(df.columns)

    if search:
        mask = df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
        df = df[mask]

    header = "".join(f"<th>{c}</th>" for c in cols)

    rows_html = ""
    for _, row in df.head(500).iterrows():
        cells = ""
        for col in cols:
            val = row[col]
            ctype = col_type(df, col)
            if pd.isna(val):
                display = "—"
            elif isinstance(val, pd.Timestamp):
                display = val.strftime("%Y-%m-%d")
            elif ctype == "FLOAT":
                display = f"{val:,.2f}"
            elif ctype == "INT":
                display = f"{int(val):,}"
            else:
                display = str(val)

            if col == pk:
                cells += f'<td class="td-pk">{display}</td>'
            elif col in fks:
                cells += f'<td class="td-fk">{display}</td>'
            elif ctype == "DATE":
                cells += f'<td class="td-dt">{display}</td>'
            elif ctype in ("INT", "FLOAT"):
                cells += f'<td class="td-num">{display}</td>'
            else:
                cells += f'<td class="td-txt">{display}</td>'
        rows_html += f"<tr>{cells}</tr>"

    html = f"""
    <div style="overflow:auto;max-height:60vh;border:1px solid #2a3040;border-radius:6px">
      <table class="db-table">
        <thead><tr>{header}</tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>"""
    return html, len(df)

# ── Schema & ERD view ─────────────────────────────────────────────────────────
def show_schema():
    st.markdown("## 📐 Schema & ERD")

    tab_erd, tab_schema, tab_rel = st.tabs(["Entity Relationship Diagram", "Schema Details", "Relationships"])

    with tab_erd:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="#141820", plot_bgcolor="#141820",
            height=520, margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(visible=False, range=[0, 10]),
            yaxis=dict(visible=False, range=[0, 7]),
            showlegend=False,
        )

        boxes = {
            "Sales Orders": (3.5, 3.5, "#3b82f6"),
            "Store":        (7.2, 5.5, "#4ade80"),
            "Budget":       (7.2, 3.5, "#f87171"),
            "Product":      (7.2, 1.5, "#fb923c"),
            "Customer":     (0.5, 1.5, "#c084fc"),
        }

        lines = [
            ("Sales Orders", "Store",    "#a78bfa"),
            ("Sales Orders", "Product",  "#a78bfa"),
            ("Sales Orders", "Customer", "#a78bfa"),
            ("Budget",       "Store",    "#a78bfa"),
        ]
        for src, dst, color in lines:
            x0, y0, _ = boxes[src]
            x1, y1, _ = boxes[dst]
            fig.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1,
                          line=dict(color=color, width=1.5, dash="dot"))
            mx, my = (x0+x1)/2, (y0+y1)/2
            fig.add_annotation(x=mx, y=my, text="N:1", showarrow=False,
                                font=dict(color="#fbbf24", size=9), bgcolor="#0f1117",
                                borderpad=2)

        col_info = {
            "Sales Orders": ["🔑 Order ID", "🔗 Customer ID", "🔗 Store ID", "🔗 Product ID",
                             "📅 Order Date", "   Order Type", "   Quantity", "   Cost", "   Sales"],
            "Store":        ["🔑 Store ID", "   Store Name", "   Channel", "   Country", "   Area Manager", "+ 8 more"],
            "Budget":       ["🔗 Store ID", "📅 Budget Date", "   Budget Sales", "   Budget Qty"],
            "Product":      ["🔑 Product ID", "   Category", "   Brand", "+ 11 more"],
            "Customer":     ["🔑 Customer ID", "   Name", "   Segment", "+ 7 more"],
        }

        for name, (xc, yc, color) in boxes.items():
            meta = TABLE_META[name]
            w, h = 2.4, 0.38 * (len(col_info[name]) + 1)
            x0, y0 = xc - w/2, yc - h/2
            fig.add_shape(type="rect", x0=x0, y0=y0, x1=x0+w, y1=y0+h,
                          line=dict(color=color, width=2), fillcolor="#0d1929")
            fig.add_shape(type="rect", x0=x0, y0=y0+h-0.38, x1=x0+w, y1=y0+h,
                          line=dict(color=color, width=0), fillcolor=meta["color"])
            fig.add_annotation(x=xc, y=y0+h-0.19, text=f"<b>{meta['type']} · {name}</b>",
                                showarrow=False, font=dict(color=meta["accent"], size=10),
                                xanchor="center")
            for i, col_txt in enumerate(col_info[name]):
                cy = y0 + h - 0.38 - 0.38*(i+1) + 0.19
                ctxt = "#fbbf24" if "🔑" in col_txt else "#a78bfa" if "🔗" in col_txt else "#34d399" if "📅" in col_txt else "#c9d4e8"
                fig.add_annotation(x=x0+0.1, y=cy, text=col_txt, showarrow=False,
                                   font=dict(color=ctxt, size=9), xanchor="left")
            fig.add_annotation(x=x0+w-0.1, y=y0+0.16, text=f"{meta['rows']} rows",
                                showarrow=False, font=dict(color="#4a5568", size=8),
                                xanchor="right")

        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            '<div style="display:flex;gap:18px;font-size:11px;color:#6b7a99;flex-wrap:wrap">'
            '<span>🟡 Primary Key</span><span style="color:#a78bfa">🟣 Foreign Key</span>'
            '<span style="color:#34d399">🟢 Date</span><span style="color:#38bdf8">🔵 Numeric</span>'
            '<span>— — FK Relationship (N:1)</span></div>',
            unsafe_allow_html=True,
        )

    with tab_schema:
        cols_ui = st.columns(3)
        for i, (name, df) in enumerate(tables.items()):
            meta = TABLE_META[name]
            pk = PK_MAP.get(name)
            fks = FK_MAP.get(name, {})
            col_rows = ""
            for col in df.columns:
                ctype = col_type(df, col)
                badge = ""
                if col == pk:
                    badge = '<span class="badge-pk">PK</span>'
                elif col in fks:
                    badge = f'<span class="badge-fk">FK→{fks[col]}</span>'
                col_rows += f'<div class="schema-col-row"><span style="color:#c9d4e8">{col}</span>{badge}<span class="badge-type">{ctype}</span></div>'
            card_html = f"""
            <div class="schema-card">
              <div class="schema-card-hdr" style="background:{meta['color']}30;color:{meta['accent']}">
                <b>{meta['icon']}</b> {name}
                <span style="margin-left:auto;font-size:10px;color:#4a5568">{meta['rows']} rows</span>
              </div>
              {col_rows}
            </div>"""
            with cols_ui[i % 3]:
                st.markdown(card_html, unsafe_allow_html=True)

    with tab_rel:
        relationships = [
            ("Sales Orders", "Store ID",    "Store",    "Store ID"),
            ("Sales Orders", "Product ID",  "Product",  "Product ID"),
            ("Sales Orders", "Customer ID", "Customer", "Customer ID"),
            ("Budget",       "Store ID",    "Store",    "Store ID"),
        ]
        for src, src_col, dst, dst_col in relationships:
            st.markdown(f"""
            <div class="rel-row">
              <span class="rel-from">{src}</span>
              <span class="rel-col">{src_col}</span>
              <span style="color:#4a5568;font-size:16px">→</span>
              <span class="rel-to">{dst}</span>
              <span class="rel-col">{dst_col}</span>
              <span class="rel-card">N : 1</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <br>
        <div style="background:#1a2030;border:1px solid #2a3040;border-radius:8px;padding:16px;font-size:12px;color:#94a3b8;line-height:1.8">
          <b style="color:#60a5fa">Star Schema</b> — two fact tables at the center:<br>
          • <b style="color:#f87171">Sales Orders</b>: 42,934 transactions → joins Store, Product, Customer<br>
          • <b style="color:#f87171">Budget</b>: 8,107 monthly targets → joins Store only<br>
          The Store dimension bridges both fact tables, enabling <b>Actual vs Target</b> analysis at store + date granularity.
        </div>""", unsafe_allow_html=True)

# ── Table data view ────────────────────────────────────────────────────────────
def show_table(name):
    meta = TABLE_META[name]
    df   = tables[name]
    fks  = FK_MAP.get(name, {})

    c1, c2, c3, c4 = st.columns([3, 1, 1, 2])
    with c1:
        st.markdown(
            f'<span style="color:{meta["accent"]};font-size:18px;font-weight:700">'
            f'{meta["icon"]} {name}</span>'
            f' <span style="background:{meta["color"]};color:{meta["accent"]};'
            f'font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px">'
            f'{meta["type"]}</span>',
            unsafe_allow_html=True,
        )
    with c2:
        st.metric("Total Rows", meta["rows"])
    with c3:
        st.metric("Columns", len(df.columns))
    with c4:
        search = st.text_input("🔍 Search", placeholder="Filter rows...", label_visibility="collapsed")

    if fks:
        with st.expander("🔗 Foreign Keys"):
            for col, ref_table in fks.items():
                st.markdown(
                    f'`{col}` → **{ref_table}** &nbsp;&nbsp;'
                    f'<span style="font-size:11px;color:#6b7a99">({df[col].nunique()} unique values)</span>',
                    unsafe_allow_html=True,
                )

    html, count = render_table(name, df, search)
    st.markdown(html, unsafe_allow_html=True)

    st.markdown(
        f'<div style="display:flex;justify-content:space-between;margin-top:6px;font-size:11px">'
        f'<span style="color:#6b7a99">🟡 PK &nbsp; 🟣 FK &nbsp; 🟢 Date &nbsp; 🔵 Numeric</span>'
        f'<span style="color:#4a5568">Showing {min(count,500):,} / {count:,} rows</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.expander("📊 Column Statistics"):
        num_cols = [c for c in df.columns if col_type(df, c) in ("INT", "FLOAT")]
        if num_cols:
            st.dataframe(df[num_cols].describe().round(2), use_container_width=True)
        else:
            st.write("No numeric columns.")

# ── Routing ───────────────────────────────────────────────────────────────────
if view == "📐 Schema & ERD":
    show_schema()
else:
    show_table(LABEL_MAP[view])
