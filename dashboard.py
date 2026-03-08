"""
Intersport · C-Suite Sales Dashboard
Power BI-style · Streamlit · Self-contained (synthetic data, no upload needed)
"""
import time
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Intersport · Sales Dashboard",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# THEME & STYLES  — consistent light mode (Power BI-inspired)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Global font & page background ── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
}
.block-container {
    padding: 1rem 1.5rem 1rem 1.5rem;
    max-width: 100%;
    background: #F0F2F6;
}

/* ── Sidebar — light ── */
section[data-testid="stSidebar"] > div:first-child {
    background: #FFFFFF !important;
    border-right: 1px solid #E1DFDD;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: #252423 !important;
}
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label {
    background: #F0F2F6;
    border-radius: 6px;
    padding: 7px 12px;
    margin-bottom: 3px;
    font-size: 13px;
    font-weight: 500;
    color: #252423 !important;
    border: 1px solid transparent;
    transition: all .15s;
}
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover {
    background: #E1EBF7;
    border-color: #0078D4;
}
section[data-testid="stSidebar"] hr {
    border-color: #E1DFDD;
}
/* Sidebar filter labels */
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSelectbox label {
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: .5px;
    color: #605E5C !important;
}

/* ── KPI metric cards ── */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 14px 18px 12px 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
    border-top: 3px solid #0078D4;
}
div[data-testid="stMetric"] > label {
    font-size: 10px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: .6px;
    color: #605E5C !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #252423 !important;
}
div[data-testid="stMetricDelta"] svg { vertical-align: middle; }

/* ── Chart cards ── */
div[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,.07);
    padding: 6px;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    background: #FFFFFF;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,.07);
    padding: 4px;
}

/* ── Page headers ── */
.pg-title {
    font-size: 20px; font-weight: 700;
    color: #252423; margin-bottom: 0;
}
.pg-sub {
    font-size: 11px; color: #605E5C;
    margin-bottom: 10px; letter-spacing: .3px;
}
.sec-lbl {
    font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
    color: #A19F9D; margin: 18px 0 6px 0;
    border-bottom: 1px solid #E1DFDD;
    padding-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# COLOUR PALETTE  — consistent light-mode tokens
# ══════════════════════════════════════════════════════════════════════════════
C = dict(
    blue   = "#0078D4",   # Power BI primary
    navy   = "#003966",   # deep accent
    green  = "#107C10",   # success / positive
    red    = "#D13438",   # danger / negative
    amber  = "#FF8C00",   # warning / budget line
    purple = "#744DA9",
    teal   = "#008272",
    grey   = "#605E5C",   # body text secondary
    bg     = "#FFFFFF",   # card/chart background
    page   = "#F0F2F6",   # page background
    grid   = "#F0F2F6",   # chart gridlines
    border = "#E1DFDD",   # subtle borders
)

# Shared Plotly layout defaults — white cards, light grid
CHART = dict(
    plot_bgcolor  = C["bg"],
    paper_bgcolor = C["bg"],
    margin        = dict(t=36, b=14, l=6, r=6),
    font          = dict(size=11, color="#252423", family="Segoe UI, sans-serif"),
)


# ══════════════════════════════════════════════════════════════════════════════
# REAL DATA LOADING  — from parquet files committed to the repo
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⏳ Loading dataset…")
def generate_data():
    import os
    base = os.path.join(os.path.dirname(__file__), "data")

    sales    = pd.read_parquet(f"{base}/sales.parquet")
    budget   = pd.read_parquet(f"{base}/budget.parquet")
    store    = pd.read_parquet(f"{base}/store.parquet")
    product  = pd.read_parquet(f"{base}/product.parquet")
    customer = pd.read_parquet(f"{base}/customer.parquet")

    # Ensure Quarter column is a string like "Q1"
    if "Quarter" not in sales.columns:
        sales["Quarter"] = "Q" + sales["Order Date"].dt.quarter.astype(str)
    else:
        sales["Quarter"] = "Q" + sales["Quarter"].astype(str)

    return dict(sales=sales, budget=budget, store=store,
                product=product, customer=customer)


# ── DEAD CODE BELOW (kept for reference only — not executed) ─────────────────


# load once
_t0 = time.perf_counter()
DATA = generate_data()

_load_ms = (time.perf_counter() - _t0) * 1000

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def fmt(v, mode="$"):
    if mode == "$":
        if abs(v) >= 1_000_000: return f"${v/1_000_000:.2f}M"
        if abs(v) >= 1_000:     return f"${v/1_000:.1f}K"
        return f"${v:,.0f}"
    s = "+" if v >= 0 else ""
    return f"{s}{v:.1f}%"


def calc_kpis(df, bgt=None):
    """
    Compute all 12 standard KPIs from a sales DataFrame.
    AOV excludes return orders from the denominator (per spec).
    """
    s_rows = df[df["Order Type"] == "Sales"]
    r_rows = df[df["Order Type"] == "Return"]

    gross_sales   = s_rows["Sales"].sum()                       # KPI 1
    return_sales  = r_rows["Sales"].sum()                       # KPI 2
    net_sales     = gross_sales - abs(return_sales)             # KPI 3

    cogs          = s_rows["Cost"].sum()                        # KPI 4
    return_cost   = r_rows["Cost"].sum()                        # KPI 5
    net_cogs      = cogs - abs(return_cost)                     # KPI 6

    gross_profit  = net_sales - net_cogs                        # KPI 7
    profit_margin = (gross_profit / net_sales * 100
                     if net_sales else 0)                       # KPI 8

    total_orders  = s_rows["Order ID"].nunique()                # KPI 9 — sales orders only
    aov           = net_sales / total_orders if total_orders else 0  # KPI 10
    units_per_ord = (s_rows["Quantity"].sum() / total_orders
                     if total_orders else 0)                    # KPI 11

    return_rate   = (abs(return_sales) / gross_sales * 100
                     if gross_sales else 0)                     # KPI 12

    out = dict(
        gross_sales=gross_sales, return_sales=return_sales,
        net_sales=net_sales, cogs=cogs, return_cost=return_cost,
        net_cogs=net_cogs, gross_profit=gross_profit,
        profit_margin=profit_margin, total_orders=total_orders,
        aov=aov, units_per_order=units_per_ord,
        return_rate=return_rate,
    )
    if bgt is not None:
        tot_b = bgt["Budget Sales"].sum()
        out["budget"]  = tot_b
        out["vs_bgt"]  = (net_sales / tot_b - 1) * 100 if tot_b else 0
        out["vs_bgt_abs"] = net_sales - tot_b
    return out


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR  — navigation + filters
# ══════════════════════════════════════════════════════════════════════════════
store_raw   = DATA["store"]
product_raw = DATA["product"]
customer_raw= DATA["customer"]
sales_raw   = DATA["sales"]
budget_raw  = DATA["budget"]

with st.sidebar:
    # ── Brand header ──────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding:8px 0 12px 0; border-bottom:1px solid #E1DFDD; margin-bottom:12px;">
            <div style="font-size:18px; font-weight:700; color:#0078D4; line-height:1.2;">🏪 Intersport</div>
            <div style="font-size:11px; color:#605E5C; font-weight:500; letter-spacing:.4px;">
                C-SUITE SALES DASHBOARD
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "nav", ["Executive Summary","Sales Performance",
                "Product & Category","Store Network",
                "Insights & Actions"],
        label_visibility="collapsed",
    )

    st.markdown(
        '<p style="font-size:10px;font-weight:700;text-transform:uppercase;'
        'letter-spacing:1px;color:#A19F9D;margin:18px 0 8px 0;'
        'border-bottom:1px solid #E1DFDD;padding-bottom:4px;">Filters</p>',
        unsafe_allow_html=True,
    )

    all_years    = sorted(sales_raw["Year"].unique())
    all_countries= sorted(store_raw["Store Country"].unique())
    all_channels = sorted(store_raw["Store Channel"].unique())
    all_cats     = sorted(product_raw["Category"].unique())

    sel_years    = st.multiselect("Year",     all_years,     default=all_years)
    sel_countries= st.multiselect("Country",  all_countries, default=all_countries)
    sel_channels = st.multiselect("Channel",  all_channels,  default=all_channels)
    sel_cats     = st.multiselect("Category", all_cats,      default=all_cats)

    # ── Technical Performance Panel ───────────────────────────────────────────
    with st.expander("⚙️ Technical Performance", expanded=False):
        _sr = DATA["sales"]
        _br = DATA["budget"]
        _st = DATA["store"]
        _pr = DATA["product"]
        _cr = DATA["customer"]
        st.markdown(f"""
<div style="font-size:11px;line-height:1.8;color:#252423;">
<b>Data Load</b><br>
⏱ <b>{_load_ms:.0f} ms</b> (cached after first run)<br>
💾 Cache: <code>@st.cache_data</code> active<br>
<br><b>Dataset Sizes</b><br>
📦 Sales rows: <b>{len(_sr):,}</b><br>
💰 Budget rows: <b>{len(_br):,}</b><br>
🏪 Stores: <b>{_st['Store ID'].nunique()}</b><br>
🛍 SKUs: <b>{_pr['Product ID'].nunique():,}</b><br>
👤 Customers: <b>{_cr['Customer ID'].nunique():,}</b><br>
<br><b>Date Range</b><br>
📅 {_sr['Order Date'].min().date()} → {_sr['Order Date'].max().date()}<br>
<br><b>Data Quality</b><br>
✅ Null sales: {_sr['Net Sales'].isna().sum()}<br>
✅ Null qty: {_sr['Net Qty'].isna().sum()}<br>
✅ Orphan orders: {_sr[~_sr['Store ID'].isin(_st['Store ID'])].shape[0]}<br>
✅ Orphan products: {_sr[~_sr['Product ID'].isin(_pr['Product ID'])].shape[0]}<br>
<br><b>Return Rate</b><br>
↩ {(_sr[_sr['Order Type']=='Return']['Sales'].sum() / _sr[_sr['Order Type']=='Sales']['Sales'].sum() * 100):.2f}% of gross sales<br>
</div>""", unsafe_allow_html=True)

    st.markdown(
        '<p style="font-size:10px;color:#A19F9D;margin-top:24px;">'
        'Intersport · 2022–2025 · C-Suite</p>',
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# FILTER APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
valid_stores = store_raw.loc[
    store_raw["Store Country"].isin(sel_countries) &
    store_raw["Store Channel"].isin(sel_channels), "Store ID"
].tolist()

valid_prods = product_raw.loc[
    product_raw["Category"].isin(sel_cats), "Product ID"
].tolist()

sales = sales_raw[
    sales_raw["Year"].isin(sel_years) &
    sales_raw["Store ID"].isin(valid_stores) &
    sales_raw["Product ID"].isin(valid_prods)
].copy()

budget = budget_raw[
    budget_raw["Year"].isin(sel_years) &
    budget_raw["Store ID"].isin(valid_stores)
].copy()


def ly_net_sales():
    ly_yrs = [y - 1 for y in sel_years]
    return sales_raw[
        sales_raw["Year"].isin(ly_yrs) &
        sales_raw["Store ID"].isin(valid_stores) &
        sales_raw["Product ID"].isin(valid_prods)
    ]["Net Sales"].sum()


# ══════════════════════════════════════════════════════════════════════════════
# ██  PAGE 1 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
if page == "Executive Summary":

    st.markdown('<p class="pg-title">Executive Summary</p>', unsafe_allow_html=True)
    st.markdown('<p class="pg-sub">All figures net of returns · Filters apply globally</p>', unsafe_allow_html=True)

    # ── KPIs via standardised calc_kpis() ─────────────────────────────────────
    K   = calc_kpis(sales, budget)
    ly  = ly_net_sales()
    vs_ly = (K["net_sales"] / ly - 1) * 100 if ly else 0

    # ── 4 grouped KPI cards (financial report layout) ─────────────────────────
    vs_ly_color  = "#107C10" if vs_ly >= 0 else "#D13438"
    vs_ly_arrow  = "▲" if vs_ly >= 0 else "▼"
    vs_bgt_color = "#107C10" if K["vs_bgt"] >= 0 else "#D13438"
    vs_bgt_arrow = "▲" if K["vs_bgt"] >= 0 else "▼"

    def kpi_card(title, accent, rows, footer=None):
        """
        rows = list of (label, value, is_highlight, value_color)
        """
        inner = ""
        for i, (lbl, val, bold, col) in enumerate(rows):
            border = "border-bottom:1px solid #F0F2F6;" if i < len(rows)-1 else ""
            fs     = "18px" if bold else "14px"
            fw     = "700"  if bold else "600"
            inner += f"""
  <div style="display:flex;justify-content:space-between;align-items:baseline;
              padding:6px 0;{border}">
    <span style="font-size:12px;color:#605E5C;">{lbl}</span>
    <span style="font-size:{fs};font-weight:{fw};color:{col};">{val}</span>
  </div>"""
        foot = f'<div style="font-size:11px;color:#605E5C;margin-top:6px;">{footer}</div>' if footer else ""
        return f"""
<div style="background:#FFFFFF;border-radius:8px;padding:16px 20px;
            box-shadow:0 1px 4px rgba(0,0,0,.08);border-top:3px solid {accent};">
  <div style="font-size:10px;font-weight:700;text-transform:uppercase;
              letter-spacing:.6px;color:#A19F9D;margin-bottom:8px;">{title}</div>
  {inner}
  {foot}
</div>"""

    g1, g2, g3, g4 = st.columns(4)

    # ── Card 1: Revenue ────────────────────────────────────────────────────────
    with g1:
        st.markdown(kpi_card(
            "Revenue", "#0078D4",
            [
                ("Gross Sales",   fmt(K["gross_sales"]),  False, "#252423"),
                ("− Returns",    f"({fmt(K['return_sales'])})", False, "#D13438"),
                ("Net Sales",     fmt(K["net_sales"]),    True,  "#0078D4"),
            ],
            footer=f"Return Rate: <b>{K['return_rate']:.1f}%</b>"
        ), unsafe_allow_html=True)

    # ── Card 2: Profitability ──────────────────────────────────────────────────
    with g2:
        pm_color = "#107C10" if K["profit_margin"] >= 40 else "#FF8C00"
        st.markdown(kpi_card(
            "Profitability", "#107C10",
            [
                ("Net COGS",      fmt(K["net_cogs"]),           False, "#252423"),
                ("Gross Profit",  fmt(K["gross_profit"]),       True,  "#107C10"),
                ("Profit Margin", f"{K['profit_margin']:.1f}%", True,  pm_color),
            ]
        ), unsafe_allow_html=True)

    # ── Card 3: vs Target ─────────────────────────────────────────────────────
    with g3:
        st.markdown(kpi_card(
            "vs Target", "#FF8C00",
            [
                ("Target",       fmt(K["budget"]),          False, "#252423"),
                ("vs Target",    f"{vs_bgt_arrow} {fmt(K['vs_bgt'],'%')}", True, vs_bgt_color),
                ("Variance $",   fmt(K["vs_bgt_abs"]),      False, vs_bgt_color),
                ("LY Revenue",   fmt(ly),                   False, "#252423"),
            ],
            footer=f"vs Prior Year: <b style='color:{vs_ly_color}'>{vs_ly_arrow} {fmt(vs_ly,'%')}</b>"
        ), unsafe_allow_html=True)

    # ── Card 4: Volume & Efficiency ───────────────────────────────────────────
    with g4:
        st.markdown(kpi_card(
            "Volume & Efficiency", "#744DA9",
            [
                ("Total Orders",   f"{K['total_orders']:,}",        False, "#252423"),
                ("AOV",            fmt(K["aov"]),                   True,  "#744DA9"),
                ("Units / Order",  f"{K['units_per_order']:.2f}",   False, "#252423"),
            ],
            footer="Orders = sales transactions only (returns excluded)"
        ), unsafe_allow_html=True)

    # ── Geography: donut (revenue share) + store status bar ───────────────────
    st.markdown('<p class="sec-lbl">Geography</p>', unsafe_allow_html=True)

    cnt = (sales.merge(store_raw[["Store ID","Store Country"]], on="Store ID", how="left")
           .groupby("Store Country")["Net Sales"].sum().reset_index()
           .sort_values("Net Sales", ascending=False))
    cnt["share"] = cnt["Net Sales"] / cnt["Net Sales"].sum() * 100
    cnt["label"] = cnt["Store Country"] + "<br>" + cnt["share"].apply(lambda v: f"{v:.1f}%")
    country_order = cnt["Store Country"].tolist()
    country_colors = {c: col for c, col in zip(country_order,
                      [C["blue"], C["teal"], C["amber"], C["purple"]])}

    # Store counts per country × status (filtered to valid stores)
    st_status = (store_raw[store_raw["Store ID"].isin(valid_stores)]
                 .groupby(["Store Country","Store Status"])["Store ID"].count()
                 .reset_index(name="Count"))
    st_total  = st_status.groupby("Store Country")["Count"].sum().reset_index(name="Total")

    geo_l, geo_r = st.columns([3, 2])

    with geo_l:
        fig_donut = go.Figure(go.Pie(
            labels=cnt["Store Country"],
            values=cnt["Net Sales"],
            text=cnt["label"],
            textinfo="text",
            hovertemplate="<b>%{label}</b><br>Revenue: %{value:$,.0f}<br>Share: %{percent}<extra></extra>",
            hole=0.55,
            marker=dict(colors=[C["blue"], C["teal"], C["amber"], C["purple"]],
                        line=dict(color="#FFFFFF", width=2)),
            sort=False,
        ))
        fig_donut.add_annotation(text="Revenue<br>Share", x=0.5, y=0.5,
                                 font=dict(size=12, color=C["grey"]), showarrow=False)
        fig_donut.update_layout(height=280, showlegend=True,
                                legend=dict(orientation="h", y=-0.08),
                                margin=dict(t=10, b=40, l=10, r=10),
                                plot_bgcolor=C["bg"], paper_bgcolor=C["bg"],
                                font=dict(size=11, color="#252423", family="Segoe UI, sans-serif"))
        st.plotly_chart(fig_donut, use_container_width=True)

    with geo_r:
        fig_stores = go.Figure()
        for status, color in [("Open", C["green"]), ("Closed", C["red"])]:
            sub = st_status[st_status["Store Status"] == status].merge(
                st_total, on="Store Country")
            # Align to country order
            sub = sub.set_index("Store Country").reindex(country_order).fillna(0).reset_index()
            fig_stores.add_trace(go.Bar(
                y=sub["Store Country"], x=sub["Count"],
                name=status, orientation="h",
                marker_color=color, opacity=0.85,
                text=sub["Count"].astype(int).astype(str),
                textposition="inside", insidetextanchor="middle",
            ))
        # Annotate total stores on the right of each bar
        for _, row in st_total.iterrows():
            fig_stores.add_annotation(
                y=row["Store Country"], x=row["Total"] + 0.2,
                text=f"<b>{int(row['Total'])} stores</b>",
                showarrow=False, xanchor="left",
                font=dict(size=11, color=C["grey"]),
            )
        fig_stores.update_layout(
            title="Stores: Open vs Closed", barmode="stack",
            height=280, xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False),
            legend=dict(orientation="h", y=-0.08),
            margin=dict(t=36, b=40, l=10, r=60),
            plot_bgcolor=C["bg"], paper_bgcolor=C["bg"],
            font=dict(size=11, color="#252423", family="Segoe UI, sans-serif"))
        st.plotly_chart(fig_stores, use_container_width=True)

    st.markdown('<p class="sec-lbl">Revenue Trend</p>', unsafe_allow_html=True)

    # ── Quarterly Revenue vs Target vs Last Year ──────────────────────────────
    # Quarter in sales is stored as "Q1","Q2"... so label = Year + " " + Quarter
    qa = (sales.groupby(["Year","Quarter"])["Net Sales"].sum().reset_index()
          .assign(Label=lambda d: d["Year"].astype(str) + " " + d["Quarter"].astype(str))
          .sort_values(["Year","Quarter"]))

    # Budget has no Quarter; derive as int then format as "Q1" to match sales
    qb = (budget.assign(Quarter="Q" + ((budget["Month"]-1)//3+1).astype(str))
          .groupby(["Year","Quarter"])["Budget Sales"].sum().reset_index()
          .assign(Label=lambda d: d["Year"].astype(str) + " " + d["Quarter"].astype(str)))

    ly_yrs = [y-1 for y in sel_years]
    max_actual_qtr = qa[["Year","Quarter"]].iloc[-1]  # last quarter with real data
    ql = (sales_raw[sales_raw["Year"].isin(ly_yrs) &
                    sales_raw["Store ID"].isin(valid_stores) &
                    sales_raw["Product ID"].isin(valid_prods)]
          .groupby(["Year","Quarter"])["Net Sales"].sum().reset_index())
    # Shift LY quarter labels +1 year so they align on the same x-axis
    ql["Year"] = ql["Year"] + 1
    # Clip to not exceed last actual quarter
    ql = ql[(ql["Year"] < max_actual_qtr["Year"]) |
            ((ql["Year"] == max_actual_qtr["Year"]) & (ql["Quarter"] <= max_actual_qtr["Quarter"]))]
    ql = ql.assign(Label=lambda d: d["Year"].astype(str) + " " + d["Quarter"].astype(str))

    q_merged = qa.merge(qb[["Label","Budget Sales"]], on="Label", how="left") \
                 .merge(ql[["Label","Net Sales"]].rename(columns={"Net Sales":"LY Sales"}), on="Label", how="left")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=q_merged["Label"], y=q_merged["Net Sales"],
        name="Revenue", marker_color=C["blue"], opacity=.85,
    ))
    fig.add_trace(go.Scatter(
        x=q_merged["Label"], y=q_merged["Budget Sales"].astype(float),
        name="Target", line=dict(color=C["amber"], width=2.5, dash="dash"),
        mode="lines+markers", marker=dict(size=7, color=C["amber"]),
        connectgaps=True,
    ))
    fig.add_trace(go.Scatter(
        x=q_merged["Label"], y=q_merged["LY Sales"].astype(float),
        name="Last Year", line=dict(color=C["grey"], width=2, dash="dot"),
        mode="lines+markers", marker=dict(size=6, color=C["grey"]),
        connectgaps=True,
    ))
    fig.update_layout(
        title="Quarterly Net Revenue vs Target vs Last Year",
        height=340,
        legend=dict(orientation="h", y=-0.22),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="$"),
        **CHART)
    st.plotly_chart(fig, use_container_width=True)

    # ── Row: Annual dual-axis + Segment donut + Channel ───────────────────────
    ca, cb, cc = st.columns([2,1.5,1.5])

    with ca:
        ya = sales.groupby("Year")["Net Sales"].sum().reset_index()
        yb = budget.groupby("Year")["Budget Sales"].sum().reset_index()
        yy = ya.merge(yb, on="Year", how="outer").sort_values("Year")
        yy["vs%"] = (yy["Net Sales"]/yy["Budget Sales"]-1)*100

        fig2 = make_subplots(specs=[[{"secondary_y":True}]])
        fig2.add_trace(go.Bar(x=yy["Year"].astype(str), y=yy["Net Sales"],
                              name="Actual", marker_color=C["blue"]), secondary_y=False)
        fig2.add_trace(go.Bar(x=yy["Year"].astype(str), y=yy["Budget Sales"],
                              name="Target", marker_color=C["amber"], opacity=.45),
                       secondary_y=False)
        fig2.add_trace(go.Scatter(x=yy["Year"].astype(str), y=yy["vs%"],
                                  name="vs Bgt %", mode="lines+markers+text",
                                  text=yy["vs%"].apply(lambda v: fmt(v,"%")),
                                  textposition="top center",
                                  line=dict(color=C["red"], width=2)),
                       secondary_y=True)
        fig2.update_layout(title="Annual Actual vs Target", barmode="group",
                           height=280, legend=dict(orientation="h",y=-0.28), **CHART)
        fig2.update_yaxes(tickprefix="$", secondary_y=False,
                          showgrid=True, gridcolor=C["grid"])
        fig2.update_yaxes(ticksuffix="%", secondary_y=True, showgrid=False)
        st.plotly_chart(fig2, use_container_width=True)

    with cb:
        seg = (sales.merge(customer_raw[["Customer ID","Customer Segment"]],
                           on="Customer ID", how="left")
               .groupby("Customer Segment")["Net Sales"].sum().reset_index())
        fig3 = px.pie(seg, values="Net Sales", names="Customer Segment",
                      title="Revenue by Segment", hole=.5,
                      color_discrete_sequence=[C["blue"],C["teal"],C["purple"],C["amber"]])
        fig3.update_traces(textinfo="percent+label", textfont_size=10)
        fig3.update_layout(height=280, showlegend=False, **CHART)
        st.plotly_chart(fig3, use_container_width=True)

    with cc:
        ch = (sales.merge(store_raw[["Store ID","Store Channel"]],on="Store ID",how="left")
              .groupby("Store Channel")["Net Sales"].sum().reset_index()
              .sort_values("Net Sales", ascending=False))
        ch["lbl"] = ch["Net Sales"].apply(fmt)
        fig4 = go.Figure(go.Bar(x=ch["Store Channel"], y=ch["Net Sales"],
                                text=ch["lbl"], textposition="outside",
                                marker_color=[C["blue"],C["teal"],C["amber"]]))
        fig4.update_layout(title="Revenue by Channel", height=280, showlegend=False,
                           yaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="$"),
                           **CHART)
        st.plotly_chart(fig4, use_container_width=True)

    # ── Q×Year heatmap ────────────────────────────────────────────────────────
    st.markdown('<p class="sec-lbl">Quarterly Heatmap</p>', unsafe_allow_html=True)
    qp = (sales.groupby(["Quarter","Year"])["Net Sales"].sum().reset_index()
          .pivot(index="Quarter", columns="Year", values="Net Sales").fillna(0))
    fhm = px.imshow(qp, text_auto=".2s", aspect="auto",
                    color_continuous_scale=["#EFF6FF","#1D4ED8"],
                    title="Net Revenue Heatmap · Quarter × Year")
    fhm.update_layout(height=200, **CHART)
    st.plotly_chart(fhm, use_container_width=True)



# ══════════════════════════════════════════════════════════════════════════════
# ██  PAGE 2 — SALES PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Sales Performance":

    st.markdown('<p class="pg-title">Sales Performance</p>', unsafe_allow_html=True)
    st.markdown('<p class="pg-sub">Growth · Target · Mix · Efficiency · Margin</p>', unsafe_allow_html=True)

    K2    = calc_kpis(sales, budget)
    ly2   = ly_net_sales()
    vs_ly2 = (K2["net_sales"] / ly2 - 1) * 100 if ly2 else 0
    avg_d  = sales[sales["Order Type"]=="Sales"]["Discount"].mean() * 100

    # ── Headline KPI strip ────────────────────────────────────────────────────
    h1,h2,h3,h4,h5 = st.columns(5)
    def _kpi(col, label, val, good=True):
        color = C["green"] if good else C["red"]
        col.markdown(f"""<div style='background:#fff;border-radius:8px;padding:14px 10px;
            border:1px solid {C["border"]};text-align:center'>
            <div style='font-size:11px;color:{C["grey"]};margin-bottom:4px'>{label}</div>
            <div style='font-size:20px;font-weight:700;color:{color}'>{val}</div>
        </div>""", unsafe_allow_html=True)
    _kpi(h1, "Net Sales",      fmt(K2["net_sales"]),        True)
    _kpi(h2, "vs Target",      fmt(K2["vs_bgt"],"%"),       K2["vs_bgt"] >= 0)
    _kpi(h3, "vs Last Year",   fmt(vs_ly2,"%"),             vs_ly2 >= 0)
    _kpi(h4, "Gross Margin",   f"{K2['profit_margin']:.1f}%", K2["profit_margin"] >= 40)
    _kpi(h5, "Return Rate",    f"{K2['return_rate']:.1f}%", K2["return_rate"] <= 15)
    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

    # ══ Q1: Are we growing? ═══════════════════════════════════════════════════
    st.markdown('<p class="sec-lbl">① Are we growing?</p>', unsafe_allow_html=True)

    fall = (sales_raw[sales_raw["Store ID"].isin(valid_stores) &
                      sales_raw["Product ID"].isin(valid_prods)]
            .groupby(["Year","Quarter"])["Net Sales"].sum().reset_index()
            .assign(Label=lambda d: d["Year"].astype(str) + " " + d["Quarter"].astype(str))
            .sort_values(["Year","Quarter"]))
    fall["YoY_abs"] = fall.groupby("Quarter")["Net Sales"].diff()
    fall["YoY%"]    = fall.groupby("Quarter")["Net Sales"].pct_change() * 100
    vis_fall = fall[fall["Year"].isin(sel_years)].copy()
    vis_fall["bar_col"] = vis_fall["YoY%"].apply(
        lambda v: C["green"] if (v is not None and v >= 0) else C["red"])

    g1, g2 = st.columns([3,2])
    with g1:
        fig_g = go.Figure()
        fig_g.add_trace(go.Bar(
            x=vis_fall["Label"], y=vis_fall["Net Sales"],
            name="Revenue", marker_color=C["blue"], opacity=.85,
            text=vis_fall["Net Sales"].apply(fmt), textposition="outside",
        ))
        # YoY % as annotations above each bar
        for _, row in vis_fall.dropna(subset=["YoY%"]).iterrows():
            arrow = "▲" if row["YoY%"] >= 0 else "▼"
            color = C["green"] if row["YoY%"] >= 0 else C["red"]
            fig_g.add_annotation(x=row["Label"],
                                 y=row["Net Sales"] * 1.12,
                                 text=f"<span style='color:{color}'>{arrow}{abs(row['YoY%']):.0f}%</span>",
                                 showarrow=False, font=dict(size=10))
        fig_g.update_layout(title="Quarterly Revenue with YoY Growth %", height=300,
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="$"),
                            **CHART)
        st.plotly_chart(fig_g, use_container_width=True)

    with g2:
        # YoY growth % bars — positive/negative waterfall feel
        yoy_q = vis_fall.dropna(subset=["YoY%"]).copy()
        fig_yoy = go.Figure(go.Bar(
            x=yoy_q["YoY%"], y=yoy_q["Label"], orientation="h",
            marker_color=yoy_q["bar_col"], opacity=.85,
            text=yoy_q["YoY%"].apply(lambda v: f"{v:+.1f}%"), textposition="outside",
        ))
        fig_yoy.add_vline(x=0, line_color="#374151", line_width=1)
        fig_yoy.update_layout(title="YoY Growth % by Quarter", height=300,
                              xaxis=dict(showgrid=False, ticksuffix="%", zeroline=False),
                              yaxis=dict(showgrid=False),
                              **CHART)
        st.plotly_chart(fig_yoy, use_container_width=True)

    # ══ Q2: Are we hitting targets? ══════════════════════════════════════════
    st.markdown('<p class="sec-lbl">② Are we hitting our targets?</p>', unsafe_allow_html=True)

    ma2 = (sales.groupby(["Year","Month"])["Net Sales"].sum().reset_index()
           .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1))))
    mb2 = (budget.groupby(["Year","Month"])["Budget Sales"].sum().reset_index()
           .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1))))
    mrg = ma2.merge(mb2, on="Date", how="outer").sort_values("Date")
    mrg["Var"]  = mrg["Net Sales"] - mrg["Budget Sales"]
    mrg["Var%"] = (mrg["Net Sales"] / mrg["Budget Sales"] - 1) * 100
    mrg["Col"]  = mrg["Var"].apply(lambda v: C["green"] if v >= 0 else C["red"])

    fig_v = make_subplots(specs=[[{"secondary_y": True}]])
    fig_v.add_trace(go.Bar(x=mrg["Date"], y=mrg["Var"],
                           marker_color=mrg["Col"], name="$ Variance", opacity=.85),
                    secondary_y=False)
    fig_v.add_trace(go.Scatter(x=mrg["Date"], y=mrg["Var%"],
                               name="% Variance", line=dict(color=C["navy"], width=1.5)),
                    secondary_y=True)
    fig_v.add_hline(y=0, line_color="#374151", line_width=1)
    fig_v.update_layout(title="Monthly Revenue Variance vs Target",
                        height=280, legend=dict(orientation="h", y=-0.22), **CHART)
    fig_v.update_yaxes(tickprefix="$", showgrid=True,  gridcolor=C["grid"], secondary_y=False)
    fig_v.update_yaxes(ticksuffix="%", showgrid=False, secondary_y=True)
    st.plotly_chart(fig_v, use_container_width=True)

    # ══ Q3: Where is growth coming from? ═════════════════════════════════════
    st.markdown('<p class="sec-lbl">③ Where is growth coming from?</p>', unsafe_allow_html=True)

    w1, w2, w3 = st.columns(3)

    with w1:
        by_country = (sales.merge(store_raw[["Store ID","Store Country"]], on="Store ID", how="left")
                      .groupby("Store Country")["Net Sales"].sum().reset_index()
                      .sort_values("Net Sales"))
        by_country["share"] = by_country["Net Sales"] / by_country["Net Sales"].sum() * 100
        fig_c = go.Figure(go.Bar(
            y=by_country["Store Country"], x=by_country["Net Sales"], orientation="h",
            marker_color=C["blue"], opacity=.85,
            text=by_country["share"].apply(lambda v: f"{v:.0f}%"), textposition="outside",
        ))
        fig_c.update_layout(title="Revenue by Country", height=240,
                            xaxis=dict(showgrid=False, tickprefix="$", showticklabels=False),
                            yaxis=dict(showgrid=False), **CHART)
        st.plotly_chart(fig_c, use_container_width=True)

    with w2:
        by_ch = (sales.merge(store_raw[["Store ID","Store Channel"]], on="Store ID", how="left")
                 .groupby("Store Channel")["Net Sales"].sum().reset_index()
                 .sort_values("Net Sales"))
        by_ch["share"] = by_ch["Net Sales"] / by_ch["Net Sales"].sum() * 100
        fig_ch = go.Figure(go.Bar(
            y=by_ch["Store Channel"], x=by_ch["Net Sales"], orientation="h",
            marker_color=C["teal"], opacity=.85,
            text=by_ch["share"].apply(lambda v: f"{v:.0f}%"), textposition="outside",
        ))
        fig_ch.update_layout(title="Revenue by Channel", height=240,
                             xaxis=dict(showgrid=False, tickprefix="$", showticklabels=False),
                             yaxis=dict(showgrid=False), **CHART)
        st.plotly_chart(fig_ch, use_container_width=True)

    with w3:
        by_cat = (sales.merge(product_raw[["Product ID","Category"]], on="Product ID", how="left")
                  .groupby("Category")["Net Sales"].sum().reset_index()
                  .sort_values("Net Sales"))
        by_cat["share"] = by_cat["Net Sales"] / by_cat["Net Sales"].sum() * 100
        fig_cat = go.Figure(go.Bar(
            y=by_cat["Category"], x=by_cat["Net Sales"], orientation="h",
            marker_color=C["purple"], opacity=.85,
            text=by_cat["share"].apply(lambda v: f"{v:.0f}%"), textposition="outside",
        ))
        fig_cat.update_layout(title="Revenue by Category", height=240,
                              xaxis=dict(showgrid=False, tickprefix="$", showticklabels=False),
                              yaxis=dict(showgrid=False), **CHART)
        st.plotly_chart(fig_cat, use_container_width=True)

    # ══ Q4: Are we selling efficiently? ══════════════════════════════════════
    st.markdown('<p class="sec-lbl">④ Are we selling efficiently?</p>', unsafe_allow_html=True)

    e1, e2, e3 = st.columns(3)

    with e1:
        # AOV by quarter
        aov_q = (sales[sales["Order Type"]=="Sales"]
                 .groupby(["Year","Quarter"])
                 .agg(Revenue=("Net Sales","sum"), Orders=("Order ID","nunique"))
                 .reset_index())
        aov_q["AOV"] = aov_q["Revenue"] / aov_q["Orders"]
        aov_q["Label"] = aov_q["Year"].astype(str) + " " + aov_q["Quarter"].astype(str)
        aov_q = aov_q[aov_q["Year"].isin(sel_years)].sort_values(["Year","Quarter"])
        fig_aov = go.Figure(go.Scatter(
            x=aov_q["Label"], y=aov_q["AOV"],
            mode="lines+markers", line=dict(color=C["blue"], width=2),
            marker=dict(size=7), fill="tozeroy", fillcolor="rgba(0,120,212,0.08)",
        ))
        fig_aov.update_layout(title="AOV Trend ($/Order)", height=230,
                              xaxis=dict(showgrid=False),
                              yaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="$"),
                              **CHART)
        st.plotly_chart(fig_aov, use_container_width=True)

    with e2:
        # Discount rate by quarter
        disc_q = (sales[sales["Order Type"]=="Sales"]
                  .groupby(["Year","Quarter"])["Discount"].mean()
                  .reset_index())
        disc_q["Disc%"] = disc_q["Discount"] * 100
        disc_q["Label"] = disc_q["Year"].astype(str) + " " + disc_q["Quarter"].astype(str)
        disc_q = disc_q[disc_q["Year"].isin(sel_years)].sort_values(["Year","Quarter"])
        disc_q["col"] = disc_q["Disc%"].apply(lambda v: C["red"] if v > 15 else C["amber"])
        fig_disc = go.Figure(go.Bar(
            x=disc_q["Label"], y=disc_q["Disc%"],
            marker_color=disc_q["col"], opacity=.85,
            text=disc_q["Disc%"].apply(lambda v: f"{v:.1f}%"), textposition="outside",
        ))
        fig_disc.add_hline(y=15, line_dash="dash", line_color=C["red"],
                           annotation_text="15% threshold", annotation_position="top right")
        fig_disc.update_layout(title="Avg Discount % by Quarter", height=230,
                               xaxis=dict(showgrid=False),
                               yaxis=dict(showgrid=True, gridcolor=C["grid"], ticksuffix="%"),
                               **CHART)
        st.plotly_chart(fig_disc, use_container_width=True)

    with e3:
        # Return rate by quarter
        ret_q = (sales_raw[sales_raw["Store ID"].isin(valid_stores) &
                           sales_raw["Year"].isin(sel_years)]
                 .groupby(["Year","Quarter","Order Type"])["Sales"].sum()
                 .reset_index())
        ret_sales = ret_q[ret_q["Order Type"]=="Sales"].rename(columns={"Sales":"Gross"})
        ret_ret   = ret_q[ret_q["Order Type"]=="Return"].rename(columns={"Sales":"Returns"})
        ret_m = ret_sales.merge(ret_ret[["Year","Quarter","Returns"]],
                                on=["Year","Quarter"], how="left").fillna(0)
        ret_m["Ret%"] = ret_m["Returns"].abs() / ret_m["Gross"] * 100
        ret_m["Label"] = ret_m["Year"].astype(str) + " " + ret_m["Quarter"].astype(str)
        ret_m = ret_m.sort_values(["Year","Quarter"])
        ret_m["col"] = ret_m["Ret%"].apply(lambda v: C["red"] if v > 20 else C["amber"])
        fig_ret2 = go.Figure(go.Bar(
            x=ret_m["Label"], y=ret_m["Ret%"],
            marker_color=ret_m["col"], opacity=.85,
            text=ret_m["Ret%"].apply(lambda v: f"{v:.1f}%"), textposition="outside",
        ))
        fig_ret2.add_hline(y=20, line_dash="dash", line_color=C["red"],
                           annotation_text="20% threshold", annotation_position="top right")
        fig_ret2.update_layout(title="Return Rate % by Quarter", height=230,
                               xaxis=dict(showgrid=False),
                               yaxis=dict(showgrid=True, gridcolor=C["grid"], ticksuffix="%"),
                               **CHART)
        st.plotly_chart(fig_ret2, use_container_width=True)

    # ══ Q5: What's the bottom line? ═══════════════════════════════════════════
    st.markdown('<p class="sec-lbl">⑤ What\'s the bottom line?</p>', unsafe_allow_html=True)

    m1, m2 = st.columns(2)

    with m1:
        # Gross Margin % by quarter
        margin_q = (sales[sales["Order Type"]=="Sales"]
                    .groupby(["Year","Quarter"])
                    .agg(Revenue=("Net Sales","sum"), Cost=("Net Cost","sum"))
                    .reset_index())
        margin_q["GM%"] = (margin_q["Revenue"] - margin_q["Cost"]) / margin_q["Revenue"] * 100
        margin_q["Label"] = margin_q["Year"].astype(str) + " " + margin_q["Quarter"].astype(str)
        margin_q = margin_q[margin_q["Year"].isin(sel_years)].sort_values(["Year","Quarter"])
        fig_gm = go.Figure(go.Scatter(
            x=margin_q["Label"], y=margin_q["GM%"],
            mode="lines+markers", line=dict(color=C["green"], width=2.5),
            marker=dict(size=7), fill="tozeroy", fillcolor="rgba(16,124,16,0.08)",
            text=margin_q["GM%"].apply(lambda v: f"{v:.1f}%"), textposition="top center",
        ))
        fig_gm.update_layout(title="Gross Margin % Trend by Quarter", height=260,
                             xaxis=dict(showgrid=False),
                             yaxis=dict(showgrid=True, gridcolor=C["grid"],
                                        ticksuffix="%", range=[0, margin_q["GM%"].max()*1.2]),
                             **CHART)
        st.plotly_chart(fig_gm, use_container_width=True)

    with m2:
        # Revenue vs Gross Profit by year — dual bar
        annual = (sales[sales["Order Type"]=="Sales"]
                  .groupby("Year")
                  .agg(Revenue=("Net Sales","sum"), Cost=("Net Cost","sum"))
                  .reset_index())
        annual["GP"] = annual["Revenue"] - annual["Cost"]
        annual["GM%"] = annual["GP"] / annual["Revenue"] * 100
        annual = annual[annual["Year"].isin(sel_years)]
        fig_ann = go.Figure()
        fig_ann.add_trace(go.Bar(x=annual["Year"].astype(str), y=annual["Revenue"],
                                 name="Revenue", marker_color=C["blue"], opacity=.7))
        fig_ann.add_trace(go.Bar(x=annual["Year"].astype(str), y=annual["GP"],
                                 name="Gross Profit", marker_color=C["green"], opacity=.85,
                                 text=annual["GM%"].apply(lambda v: f"{v:.1f}%"),
                                 textposition="outside"))
        fig_ann.update_layout(title="Annual Revenue vs Gross Profit", height=260,
                              barmode="group",
                              yaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="$"),
                              legend=dict(orientation="h", y=-0.22),
                              **CHART)
        st.plotly_chart(fig_ann, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ██  PAGE 3 — PRODUCT & CATEGORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Product & Category":

    st.markdown('<p class="pg-title">Product & Category</p>', unsafe_allow_html=True)
    st.markdown('<p class="pg-sub">Bestsellers · Slow movers · Margin by category</p>', unsafe_allow_html=True)

    ps = sales.merge(product_raw, on="Product ID", how="left")

    KP    = calc_kpis(ps)
    prods = ps["Product ID"].nunique()
    avg_d = ps[ps["Order Type"]=="Sales"]["Discount"].mean() * 100

    k1,k2,k3,k4,k5,k6,k7 = st.columns(7)
    k1.metric("Gross Sales",    fmt(KP["gross_sales"]))
    k2.metric("Net Sales",      fmt(KP["net_sales"]))
    k3.metric("Gross Profit",   fmt(KP["gross_profit"]))
    k4.metric("Profit Margin",  f"{KP['profit_margin']:.1f}%")
    k5.metric("Return Rate",    f"{KP['return_rate']:.1f}%")
    k6.metric("Unique SKUs",    f"{prods:,}")
    k7.metric("Avg Discount",   f"{avg_d:.1f}%")

    st.markdown('<p class="sec-lbl">Category Overview</p>', unsafe_allow_html=True)
    ct1, ct2 = st.columns([3,2])

    with ct1:
        sub = ps.groupby(["Category","Sub-Category"])["Net Sales"].sum().reset_index()
        fig_tm = px.treemap(sub, path=["Category","Sub-Category"], values="Net Sales",
                            color="Net Sales",
                            color_continuous_scale=["#DBEAFE","#1D4ED8"],
                            title="Revenue Treemap · Category → Sub-Category")
        fig_tm.update_layout(height=360, **CHART)
        st.plotly_chart(fig_tm, use_container_width=True)

    with ct2:
        cat = (ps.groupby("Category")
               .agg(Net_Sales=("Net Sales","sum"), Net_Cost=("Net Cost","sum"))
               .reset_index())
        cat["GM%"] = (cat["Net_Sales"]-cat["Net_Cost"])/cat["Net_Sales"]*100
        cat = cat.sort_values("Net_Sales", ascending=True)
        cat["lbl"] = cat["Net_Sales"].apply(fmt)
        fig_c = go.Figure()
        fig_c.add_trace(go.Bar(y=cat["Category"], x=cat["Net_Sales"], orientation="h",
                               name="Revenue", marker_color=C["blue"],
                               text=cat["lbl"], textposition="outside"))
        fig_c.add_trace(go.Scatter(y=cat["Category"], x=cat["GM%"],
                                   mode="markers", name="GM %", xaxis="x2",
                                   marker=dict(color=C["green"],size=11,symbol="diamond")))
        fig_c.update_layout(
            title="Revenue & GM% by Category",
            height=360,
            xaxis=dict(title="Revenue ($)", showgrid=True, gridcolor=C["grid"]),
            xaxis2=dict(title="GM %", overlaying="x", side="top",
                        ticksuffix="%", showgrid=False),
            legend=dict(orientation="h", y=-0.15), **CHART)
        st.plotly_chart(fig_c, use_container_width=True)

    st.markdown('<p class="sec-lbl">Product Ranking</p>', unsafe_allow_html=True)

    pa = (ps.groupby(["Product ID","Product Name","Category","Sub-Category",
                       "Price Tier","Lifecycle","Product Image URL"])
          .agg(Revenue=("Net Sales","sum"), Qty=("Net Qty","sum"),
               Cost=("Net Cost","sum"))
          .reset_index())
    pa["GM%"] = (pa["Revenue"]-pa["Cost"])/pa["Revenue"]*100
    pa = pa.sort_values("Revenue", ascending=False)

    _CAT_EMOJI = {
        "Football":"⚽","Running":"👟","Tennis":"🎾","Cycling":"🚴",
        "Swimming":"🏊","Basketball":"🏀","Fitness":"💪","Outdoor":"🏔️",
        "Winter Sports":"⛷️","Team Sports":"🏅",
    }

    def render_prods(df_sub, header):
        st.markdown(f"**{header}**")
        for rank, (_, r) in enumerate(df_sub.iterrows(), 1):
            a, b, c_ = st.columns([1,4,1])
            with a:
                emoji = _CAT_EMOJI.get(str(r.get("Category","")), "🏷️")
                st.markdown(
                    f'<div style="font-size:32px;text-align:center;padding:4px 0;">{emoji}</div>',
                    unsafe_allow_html=True,
                )
            with b:
                st.markdown(f"**#{rank} {r['Product Name']}**")
                st.caption(f"{r['Category']} › {r['Sub-Category']}  ·  "
                           f"{r['Price Tier']}  ·  {r['Lifecycle']}")
            with c_:
                st.markdown(f"**{fmt(r['Revenue'])}**")
                st.caption(f"GM {r['GM%']:.0f}%  ·  {int(r['Qty']):,} units")

    pb1, pb2 = st.columns(2)
    with pb1:
        render_prods(pa.head(10), "🏆 Top 10 Bestsellers")
    with pb2:
        slow = pa[pa["Revenue"] > 0].tail(10).sort_values("Revenue")
        render_prods(slow, "🐢 Bottom 10 Slow Movers")

    st.markdown('<p class="sec-lbl">Portfolio Mix</p>', unsafe_allow_html=True)
    pm1, pm2, pm3 = st.columns(3)

    with pm1:
        pt = ps.groupby("Price Tier")["Net Sales"].sum().reset_index()
        fig_pt = px.pie(pt, values="Net Sales", names="Price Tier",
                        title="Revenue by Price Tier", hole=.45,
                        color_discrete_sequence=[C["blue"],C["teal"],C["purple"]])
        fig_pt.update_layout(height=240, **CHART)
        st.plotly_chart(fig_pt, use_container_width=True)

    with pm2:
        lc = (ps.groupby("Lifecycle")["Net Sales"].sum().reset_index()
              .sort_values("Net Sales", ascending=False))
        lc["lbl"] = lc["Net Sales"].apply(fmt)
        fig_lc = go.Figure(go.Bar(x=lc["Lifecycle"], y=lc["Net Sales"],
                                  text=lc["lbl"], textposition="outside",
                                  marker_color=C["teal"]))
        fig_lc.update_layout(title="Revenue by Lifecycle", height=240,
                             yaxis=dict(showgrid=True, gridcolor=C["grid"],
                                        tickprefix="$"), **CHART)
        st.plotly_chart(fig_lc, use_container_width=True)

    with pm3:
        br = (ps.groupby("Brand")["Net Sales"].sum().reset_index()
              .sort_values("Net Sales", ascending=False).head(8)
              .sort_values("Net Sales"))
        fig_br = go.Figure(go.Bar(y=br["Brand"], x=br["Net Sales"],
                                  orientation="h", marker_color=C["purple"]))
        fig_br.update_layout(title="Top 8 Brands", height=240,
                             xaxis=dict(showgrid=True, gridcolor=C["grid"],
                                        tickprefix="$"), **CHART)
        st.plotly_chart(fig_br, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ██  PAGE 4 — STORE NETWORK
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Store Network":

    st.markdown('<p class="pg-title">Store Network</p>', unsafe_allow_html=True)
    st.markdown('<p class="pg-sub">Performance · Targets · Growth · Efficiency</p>', unsafe_allow_html=True)

    # ── Per-store KPI aggregation ─────────────────────────────────────────────
    s_only = sales[sales["Order Type"] == "Sales"]
    r_only = sales[sales["Order Type"] == "Return"]
    bgt_s  = budget.groupby("Store ID")["Budget Sales"].sum().reset_index()

    st_s = (s_only.groupby("Store ID")
            .agg(GrossSales=("Sales","sum"), COGS=("Cost","sum"),
                 SalesOrders=("Order ID","nunique"), SalesQty=("Quantity","sum"))
            .reset_index())
    st_r = (r_only.groupby("Store ID")
            .agg(ReturnSales=("Sales","sum"), ReturnCost=("Cost","sum"))
            .reset_index())
    st_agg = (st_s.merge(st_r, on="Store ID", how="left")
              .merge(store_raw[["Store ID","Store Name","Store Country",
                                "Store Channel","Store Format","Store SQM",
                                "Store Area Manager","Store LFL Status",
                                "Store Status"]], on="Store ID", how="left")
              .merge(bgt_s, on="Store ID", how="left"))
    st_agg["ReturnSales"] = st_agg["ReturnSales"].fillna(0)
    st_agg["ReturnCost"]  = st_agg["ReturnCost"].fillna(0)
    st_agg["Revenue"]     = st_agg["GrossSales"] - st_agg["ReturnSales"].abs()
    st_agg["NetCOGS"]     = st_agg["COGS"] - st_agg["ReturnCost"].abs()
    st_agg["GrossProfit"] = st_agg["Revenue"] - st_agg["NetCOGS"]
    st_agg["GM%"]         = (st_agg["GrossProfit"] / st_agg["Revenue"] * 100).fillna(0)
    st_agg["AOV"]         = st_agg["Revenue"] / st_agg["SalesOrders"]
    st_agg["Units/Order"] = st_agg["SalesQty"] / st_agg["SalesOrders"]
    st_agg["ReturnRate%"] = (st_agg["ReturnSales"].abs() / st_agg["GrossSales"] * 100).fillna(0)
    st_agg["Sales/SQM"]   = st_agg["Revenue"] / st_agg["Store SQM"]
    st_agg["vs Bgt%"]     = (st_agg["Revenue"] / st_agg["Budget Sales"] - 1) * 100

    # LY per store
    ly_yrs_s = [y-1 for y in sel_years]
    st_ly = (sales_raw[sales_raw["Year"].isin(ly_yrs_s) &
                       sales_raw["Store ID"].isin(valid_stores) &
                       (sales_raw["Order Type"]=="Sales")]
             .groupby("Store ID")["Net Sales"].sum().reset_index()
             .rename(columns={"Net Sales":"LY_Revenue"}))
    st_agg = st_agg.merge(st_ly, on="Store ID", how="left")
    st_agg["vs LY%"] = (st_agg["Revenue"] / st_agg["LY_Revenue"] - 1) * 100

    KS = calc_kpis(sales, budget)

    # ── Headline KPIs ─────────────────────────────────────────────────────────
    h1,h2,h3,h4,h5,h6 = st.columns(6)
    def _skpi(col, label, val, good=True):
        color = C["green"] if good else C["red"]
        col.markdown(f"""<div style='background:#fff;border-radius:8px;padding:12px 8px;
            border:1px solid {C["border"]};text-align:center'>
            <div style='font-size:11px;color:{C["grey"]};margin-bottom:4px'>{label}</div>
            <div style='font-size:18px;font-weight:700;color:{color}'>{val}</div>
        </div>""", unsafe_allow_html=True)
    open_n  = (st_agg["Store Status"]=="Open").sum()
    closed_n= (st_agg["Store Status"]=="Closed").sum()
    _skpi(h1, "Open / Closed",   f"{open_n} / {closed_n}",   True)
    _skpi(h2, "Net Sales",        fmt(KS["net_sales"]),        True)
    _skpi(h3, "vs Target",        fmt(KS["vs_bgt"],"%"),       KS["vs_bgt"]>=0)
    _skpi(h4, "Gross Margin",     f"{KS['profit_margin']:.1f}%", KS["profit_margin"]>=40)
    _skpi(h5, "Avg $/SQM",        f"${st_agg['Sales/SQM'].mean():.0f}", True)
    _skpi(h6, "Avg AOV",          f"${st_agg['AOV'].mean():.0f}",        True)
    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

    # ══ Q1: Which stores are making money? ════════════════════════════════════
    st.markdown('<p class="sec-lbl">① Which stores are making money?</p>', unsafe_allow_html=True)

    q1a, q1b = st.columns(2)
    with q1a:
        top5  = st_agg.nlargest(5,  "Revenue")[["Store Name","Revenue","GM%","Store Country"]].copy()
        bot5  = st_agg.nsmallest(5, "Revenue")[["Store Name","Revenue","GM%","Store Country"]].copy()
        top5["rank"] = [f"#{i}" for i in range(1,6)]
        bot5["rank"] = [f"#{i}" for i in range(len(st_agg), len(st_agg)-5, -1)]
        top5["type"] = "Top 5"
        bot5["type"] = "Bottom 5"
        tb = pd.concat([top5, bot5])
        colors = [C["blue"] if t=="Top 5" else C["red"] for t in tb["type"]]
        fig_tb = go.Figure(go.Bar(
            y=tb["Store Name"], x=tb["Revenue"], orientation="h",
            marker_color=colors, opacity=.85,
            text=tb.apply(lambda r: f"{fmt(r['Revenue'])}  GM {r['GM%']:.0f}%", axis=1),
            textposition="outside",
        ))
        fig_tb.update_layout(title="Top 5 vs Bottom 5 Stores by Revenue",
                             height=360,
                             xaxis=dict(showgrid=False, showticklabels=False),
                             yaxis=dict(showgrid=False),
                             **CHART)
        st.plotly_chart(fig_tb, use_container_width=True)

    with q1b:
        fig_sc = px.scatter(
            st_agg, x="Revenue", y="GM%",
            size="Revenue", color="Store Country",
            hover_name="Store Name",
            title="Revenue vs Gross Margin % (bubble = revenue size)",
            size_max=40,
            color_discrete_sequence=[C["blue"],C["teal"],C["amber"],C["purple"]],
        )
        fig_sc.add_hline(y=st_agg["GM%"].mean(), line_dash="dot",
                         line_color=C["grey"], opacity=.5,
                         annotation_text="Avg GM%", annotation_position="right")
        fig_sc.update_layout(height=360,
                             xaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="$"),
                             yaxis=dict(showgrid=True, gridcolor=C["grid"], ticksuffix="%"),
                             **CHART)
        st.plotly_chart(fig_sc, use_container_width=True)

    # ══ Q2: Which stores are hitting their targets? ═══════════════════════════
    st.markdown('<p class="sec-lbl">② Which stores are hitting their targets?</p>', unsafe_allow_html=True)

    st_bgt = st_agg.dropna(subset=["vs Bgt%"]).sort_values("vs Bgt%")
    st_bgt["col"] = st_bgt["vs Bgt%"].apply(lambda v: C["green"] if v >= 0 else C["red"])
    st_bgt["lbl"] = st_bgt["vs Bgt%"].apply(lambda v: f"{v:+.1f}%")

    fig_bgt = go.Figure(go.Bar(
        y=st_bgt["Store Name"], x=st_bgt["vs Bgt%"], orientation="h",
        marker_color=st_bgt["col"], opacity=.85,
        text=st_bgt["lbl"], textposition="outside",
    ))
    fig_bgt.add_vline(x=0, line_color="#374151", line_width=1.5)
    fig_bgt.update_layout(title="All Stores · vs Target % (green = above, red = below)",
                          height=560,
                          xaxis=dict(showgrid=False, ticksuffix="%", zeroline=False),
                          yaxis=dict(showgrid=False),
                          **CHART)
    st.plotly_chart(fig_bgt, use_container_width=True)

    # ══ Q3: Are stores growing? ══════════════════════════════════════════════
    st.markdown('<p class="sec-lbl">③ Are stores growing?</p>', unsafe_allow_html=True)

    st_ly_chart = st_agg.dropna(subset=["vs LY%"]).sort_values("vs LY%")
    st_ly_chart["col"] = st_ly_chart["vs LY%"].apply(lambda v: C["green"] if v >= 0 else C["red"])
    st_ly_chart["lbl"] = st_ly_chart["vs LY%"].apply(lambda v: f"{v:+.1f}%")

    fig_ly = go.Figure(go.Bar(
        y=st_ly_chart["Store Name"], x=st_ly_chart["vs LY%"], orientation="h",
        marker_color=st_ly_chart["col"], opacity=.85,
        text=st_ly_chart["lbl"], textposition="outside",
    ))
    fig_ly.add_vline(x=0, line_color="#374151", line_width=1.5)
    fig_ly.update_layout(title="All Stores · vs Last Year % (green = growing, red = declining)",
                         height=560,
                         xaxis=dict(showgrid=False, ticksuffix="%", zeroline=False),
                         yaxis=dict(showgrid=False),
                         **CHART)
    st.plotly_chart(fig_ly, use_container_width=True)

    # ══ Q4: Are stores operating efficiently? ════════════════════════════════
    st.markdown('<p class="sec-lbl">④ Are stores operating efficiently?</p>', unsafe_allow_html=True)

    ef1, ef2, ef3 = st.columns(3)

    with ef1:
        sqm = st_agg.sort_values("Sales/SQM", ascending=True)
        sqm["col"] = sqm["Sales/SQM"].apply(
            lambda v: C["green"] if v >= sqm["Sales/SQM"].median() else C["amber"])
        fig_sqm = go.Figure(go.Bar(
            y=sqm["Store Name"], x=sqm["Sales/SQM"], orientation="h",
            marker_color=sqm["col"], opacity=.85,
        ))
        fig_sqm.add_vline(x=sqm["Sales/SQM"].median(), line_dash="dot",
                          line_color=C["grey"], opacity=.6,
                          annotation_text="Median", annotation_position="top")
        fig_sqm.update_layout(title="Revenue per SQM ($/m²)", height=560,
                              xaxis=dict(showgrid=False, tickprefix="$", showticklabels=False),
                              yaxis=dict(showgrid=False),
                              **CHART)
        st.plotly_chart(fig_sqm, use_container_width=True)

    with ef2:
        aov_s = st_agg.sort_values("AOV", ascending=True)
        aov_s["col"] = aov_s["AOV"].apply(
            lambda v: C["green"] if v >= aov_s["AOV"].median() else C["amber"])
        fig_aov = go.Figure(go.Bar(
            y=aov_s["Store Name"], x=aov_s["AOV"], orientation="h",
            marker_color=aov_s["col"], opacity=.85,
        ))
        fig_aov.add_vline(x=aov_s["AOV"].median(), line_dash="dot",
                          line_color=C["grey"], opacity=.6,
                          annotation_text="Median", annotation_position="top")
        fig_aov.update_layout(title="AOV — Avg Order Value ($/order)", height=560,
                              xaxis=dict(showgrid=False, tickprefix="$", showticklabels=False),
                              yaxis=dict(showgrid=False),
                              **CHART)
        st.plotly_chart(fig_aov, use_container_width=True)

    with ef3:
        ret_s = st_agg.sort_values("ReturnRate%", ascending=False)
        ret_s["col"] = ret_s["ReturnRate%"].apply(
            lambda v: C["red"] if v > 20 else (C["amber"] if v > 15 else C["green"]))
        fig_rr = go.Figure(go.Bar(
            y=ret_s["Store Name"], x=ret_s["ReturnRate%"], orientation="h",
            marker_color=ret_s["col"], opacity=.85,
            text=ret_s["ReturnRate%"].apply(lambda v: f"{v:.1f}%"), textposition="outside",
        ))
        fig_rr.add_vline(x=20, line_dash="dash", line_color=C["red"], opacity=.5,
                         annotation_text="20% alert", annotation_position="top")
        fig_rr.update_layout(title="Return Rate % per Store", height=560,
                              xaxis=dict(showgrid=False, ticksuffix="%", showticklabels=False),
                              yaxis=dict(showgrid=False),
                              **CHART)
        st.plotly_chart(fig_rr, use_container_width=True)

    # ══ Area Manager accountability ═══════════════════════════════════════════
    st.markdown('<p class="sec-lbl">Area Manager Accountability</p>', unsafe_allow_html=True)
    am_agg = (st_agg.groupby("Store Area Manager")
              .agg(Revenue=("Revenue","sum"),
                   Budget=("Budget Sales","sum"),
                   Stores=("Store ID","count"))
              .reset_index())
    am_agg["vs Tgt%"] = (am_agg["Revenue"] / am_agg["Budget"] - 1) * 100
    am_agg = am_agg.sort_values("vs Tgt%")
    am_agg["col"] = am_agg["vs Tgt%"].apply(lambda v: C["green"] if v >= 0 else C["red"])

    fig_am = go.Figure()
    fig_am.add_trace(go.Bar(
        x=am_agg["Store Area Manager"], y=am_agg["Revenue"],
        name="Revenue", marker_color=C["blue"], opacity=.8,
        text=am_agg["Revenue"].apply(fmt), textposition="outside",
    ))
    fig_am.add_trace(go.Scatter(
        x=am_agg["Store Area Manager"], y=am_agg["vs Tgt%"],
        name="vs Target %", yaxis="y2", mode="markers+text",
        marker=dict(color=am_agg["col"], size=14, symbol="diamond"),
        text=am_agg["vs Tgt%"].apply(lambda v: f"{v:+.1f}%"),
        textposition="top center", textfont=dict(size=10),
    ))
    fig_am.update_layout(
        title="Area Manager · Revenue & vs Target %",
        height=300,
        yaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="$"),
        yaxis2=dict(overlaying="y", side="right", ticksuffix="%",
                    showgrid=False, zeroline=False),
        legend=dict(orientation="h", y=-0.2),
        **CHART)
    st.plotly_chart(fig_am, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# ██  PAGE 5 — INSIGHTS & ACTIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Insights & Actions":

    st.markdown('<p class="pg-title">Insights & Actions</p>', unsafe_allow_html=True)
    st.markdown('<p class="pg-sub">Rule-based recommendations derived from live dashboard data · Updated on every filter change</p>',
                unsafe_allow_html=True)

    # ── Compute signals via standardised calc_kpis() ──────────────────────────
    KI     = calc_kpis(sales, budget)
    ly_i   = ly_net_sales()
    vs_b   = KI["vs_bgt"]
    vs_ly  = (KI["net_sales"] / ly_i - 1) * 100 if ly_i else 0
    ret_rt = KI["return_rate"]
    avg_disc = sales[sales["Order Type"]=="Sales"]["Discount"].mean() * 100

    # Store-level
    bgt_s  = budget.groupby("Store ID")["Budget Sales"].sum().reset_index()
    st_agg = (sales.groupby("Store ID")
              .agg(Revenue=("Net Sales","sum"), Cost=("Net Cost","sum"),
                   Qty=("Net Qty","sum"), Txn=("Order ID","nunique"))
              .reset_index()
              .merge(store_raw[["Store ID","Store Name","Store Country",
                                "Store Channel","Store Status"]], on="Store ID", how="left")
              .merge(bgt_s, on="Store ID", how="left"))
    st_agg["vs_bgt"]  = (st_agg["Revenue"] / st_agg["Budget Sales"] - 1) * 100
    # Gross Profit = Net Sales − Net COGS; GM% = Gross Profit / Net Sales
    st_agg["GM%"]     = (st_agg["Revenue"] - st_agg["Cost"]) / st_agg["Revenue"] * 100

    below_bgt = st_agg[st_agg["vs_bgt"] < -10].sort_values("vs_bgt")
    above_bgt = st_agg[st_agg["vs_bgt"] > 15].sort_values("vs_bgt", ascending=False)
    low_gm    = st_agg[st_agg["GM%"] < 30].sort_values("GM%")

    # Category YoY
    ps = sales.merge(product_raw, on="Product ID", how="left")
    cat_yr = (sales_raw.merge(product_raw[["Product ID","Category"]], on="Product ID", how="left")
              .groupby(["Category","Year"])["Net Sales"].sum().reset_index())
    if len(sel_years) >= 1:
        cur_yr  = max(sel_years)
        prev_yr = cur_yr - 1
        cat_cur  = cat_yr[cat_yr["Year"]==cur_yr].rename(columns={"Net Sales":"cur"})
        cat_prev = cat_yr[cat_yr["Year"]==prev_yr].rename(columns={"Net Sales":"prev"})
        cat_yoy  = cat_cur.merge(cat_prev, on="Category", how="outer").fillna(0)
        cat_yoy["yoy%"] = (cat_yoy["cur"] / cat_yoy["prev"] - 1) * 100
        cat_decline = cat_yoy[(cat_yoy["yoy%"] < -5) & (cat_yoy["prev"] > 0)].sort_values("yoy%")
    else:
        cat_decline = pd.DataFrame()

    # Monthly outliers
    ma_i = (sales.groupby(["Year","Month"])["Net Sales"].sum().reset_index()
            .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1)))
            .sort_values("Date"))
    if len(ma_i) >= 4:
        q1i, q3i = ma_i["Net Sales"].quantile([0.25, 0.75])
        iqri = q3i - q1i
        outliers_i = ma_i[(ma_i["Net Sales"] < q1i - 1.5*iqri) | (ma_i["Net Sales"] > q3i + 1.5*iqri)]
    else:
        outliers_i = pd.DataFrame()

    def card(color, icon, title, body):
        border = {"🔴":"#D13438","🟡":"#FF8C00","🟢":"#107C10"}.get(icon, "#0078D4")
        st.markdown(f"""
<div style="background:#FFFFFF;border-left:4px solid {border};border-radius:6px;
            padding:14px 18px;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,.07);">
  <div style="font-size:13px;font-weight:700;color:#252423;">{icon} {title}</div>
  <div style="font-size:12px;color:#605E5C;margin-top:4px;line-height:1.6;">{body}</div>
</div>""", unsafe_allow_html=True)

    # ── Section: Revenue vs Target ─────────────────────────────────────────────
    st.markdown('<p class="sec-lbl">Revenue vs Target</p>', unsafe_allow_html=True)

    if vs_b < -10:
        card("🔴","🔴","Revenue Critically Below Budget",
             f"Net revenue is <b>{fmt(vs_b,'%')}</b> vs budget ({fmt(KI['net_sales'])} vs {fmt(KI['budget'])}). "
             f"Immediate review of pricing, campaign spend, and channel mix required.")
    elif vs_b < 0:
        card("🟡","🟡","Revenue Below Budget — Monitor Closely",
             f"Net revenue is <b>{fmt(vs_b,'%')}</b> vs budget. "
             f"Review underperforming stores and activate promotional levers.")
    else:
        card("🟢","🟢","Revenue On or Ahead of Budget",
             f"Net revenue is <b>{fmt(vs_b,'%')}</b> vs budget. "
             f"Sustain momentum; consider raising Q4 budget targets.")

    if vs_ly < -5:
        card("🔴","🔴","Year-on-Year Revenue Declining",
             f"Revenue is <b>{fmt(vs_ly,'%')}</b> vs prior year. "
             f"Investigate whether this is market-driven, assortment-related, or store-specific.")
    elif vs_ly >= 5:
        card("🟢","🟢","Strong Year-on-Year Growth",
             f"Revenue grew <b>{fmt(vs_ly,'%')}</b> vs prior year ({fmt(ly_i)} → {fmt(KI['net_sales'])}). "
             f"Identify best-practice stores and scale their playbook.")

    # ── Section: Store Actions ─────────────────────────────────────────────────
    st.markdown('<p class="sec-lbl">Store Actions</p>', unsafe_allow_html=True)

    if not below_bgt.empty:
        names = ", ".join(below_bgt["Store Name"].head(3).tolist())
        card("🔴","🔴",f"{len(below_bgt)} Store(s) >10% Below Budget",
             f"<b>{names}</b> and {max(0,len(below_bgt)-3)} others are materially missing budget. "
             f"Assign area manager reviews, check local trading conditions and competitor activity.")
    if not above_bgt.empty:
        names2 = ", ".join(above_bgt["Store Name"].head(3).tolist())
        card("🟢","🟢",f"{len(above_bgt)} Store(s) >15% Above Budget",
             f"<b>{names2}</b> are significantly outperforming. "
             f"Share best practices, consider budget uplift, and explore local replication.")
    if not low_gm.empty:
        names3 = ", ".join(low_gm["Store Name"].head(3).tolist())
        card("🟡","🟡",f"{len(low_gm)} Store(s) with Gross Margin < 30%",
             f"<b>{names3}</b> have margin pressure. Review discount authorisation levels "
             f"and cost allocations.")

    # ── Section: Product & Category ────────────────────────────────────────────
    st.markdown('<p class="sec-lbl">Product & Category</p>', unsafe_allow_html=True)

    if not cat_decline.empty:
        dec_list = ", ".join(
            f"{r['Category']} ({r['yoy%']:+.0f}%)"
            for _, r in cat_decline.head(3).iterrows()
        )
        card("🟡","🟡","Declining Categories — Action Needed",
             f"YoY decline in: <b>{dec_list}</b>. "
             f"Review assortment relevance, pricing vs competitors, and in-store presentation.")

    slow_gm = ps.groupby("Product ID").agg(
        Revenue=("Net Sales","sum"), Cost=("Net Cost","sum"),
        Name=("Product Name","first")
    ).reset_index()
    slow_gm["GM%"] = (slow_gm["Revenue"] - slow_gm["Cost"]) / slow_gm["Revenue"] * 100
    neg_gm_prods = slow_gm[slow_gm["GM%"] < 0]
    if not neg_gm_prods.empty:
        card("🔴","🔴",f"{len(neg_gm_prods)} SKU(s) with Negative Gross Margin",
             f"These products are selling below cost. Review pricing, clearance strategy, "
             f"or discontinue if lifecycle is End-of-Life.")

    if avg_disc > 15:
        card("🟡","🟡",f"Average Discount at {avg_disc:.1f}% — Review Promotional Strategy",
             f"High blanket discounting erodes margin. Shift to targeted, customer-segment "
             f"promotions and enforce discount approval thresholds.")
    else:
        card("🟢","🟢",f"Discount Level Controlled at {avg_disc:.1f}%",
             f"Promotional discipline is sound. Maintain guardrails and reward high-margin sales.")

    # ── Section: Returns ───────────────────────────────────────────────────────
    st.markdown('<p class="sec-lbl">Returns</p>', unsafe_allow_html=True)

    if ret_rt > 12:
        card("🔴","🔴",f"Return Rate {ret_rt:.1f}% — Requires Immediate Investigation",
             f"Return rate above 12% threshold. Investigate product quality issues, "
             f"sizing accuracy, misleading product descriptions, and channel-specific patterns.")
    elif ret_rt > 8:
        card("🟡","🟡",f"Return Rate {ret_rt:.1f}% — Elevated",
             f"Monitor closely. Identify top-returning SKUs and channels. "
             f"Ensure return data feeds back into buying decisions.")
    else:
        card("🟢","🟢",f"Return Rate {ret_rt:.1f}% — Healthy",
             f"Returns are within acceptable range. Continue monitoring for seasonal spikes.")

    # ── Section: Trend Anomalies ───────────────────────────────────────────────
    st.markdown('<p class="sec-lbl">Trend Anomalies Detected</p>', unsafe_allow_html=True)

    if not outliers_i.empty:
        for _, row in outliers_i.iterrows():
            direction = "spike" if row["Net Sales"] > ma_i["Net Sales"].median() else "dip"
            month_lbl = row["Date"].strftime("%b %Y")
            card("🟡","🟡",f"Statistical {direction.title()} in {month_lbl}",
                 f"Revenue of <b>{fmt(row['Net Sales'])}</b> is an outlier (±1.5 IQR). "
                 f"Investigate {'one-off promotional event or exceptional trading conditions' if direction=='spike' else 'supply disruption, store closure, or external shock'}.")
    else:
        card("🟢","🟢","No Statistical Outliers Detected",
             "Monthly revenue is tracking within normal bounds for the selected period.")

    # ── Section: Prioritised Action Table ─────────────────────────────────────
    st.markdown('<p class="sec-lbl">Prioritised Action Summary</p>', unsafe_allow_html=True)

    actions = []
    if vs_b < -10:          actions.append(("🔴 Critical","Revenue vs Target","Activate recovery plan: pricing, promotions, store reviews","CFO / Commercial Director"))
    elif vs_b < 0:          actions.append(("🟡 Monitor","Revenue vs Target","Weekly target variance review with area managers","Commercial Director"))
    if vs_ly < -5:          actions.append(("🔴 Critical","YoY Growth","Root-cause analysis of YoY decline by country and channel","CEO / Strategy"))
    if not below_bgt.empty: actions.append(("🔴 Critical","Store Performance",f"Area manager reviews for {len(below_bgt)} underperforming stores","Area Managers"))
    if not low_gm.empty:    actions.append(("🟡 Monitor","Store Margin",f"Margin improvement plans for {len(low_gm)} low-GM stores","Finance / Ops"))
    if not cat_decline.empty: actions.append(("🟡 Monitor","Category Mix","Assortment refresh for declining categories","Buying / Merchandising"))
    if not neg_gm_prods.empty: actions.append(("🔴 Critical","Negative GM SKUs",f"Clearance or discontinuation of {len(neg_gm_prods)} loss-making SKUs","Buying"))
    if avg_disc > 15:       actions.append(("🟡 Monitor","Discounting","Implement discount approval guardrails","Commercial Director"))
    if ret_rt > 12:         actions.append(("🔴 Critical","Return Rate","Launch quality/product accuracy investigation","Quality / Ops"))
    elif ret_rt > 8:        actions.append(("🟡 Monitor","Return Rate","Monthly returns SKU analysis","Buying"))
    if not outliers_i.empty: actions.append(("🟡 Monitor","Revenue Anomalies",f"Investigate {len(outliers_i)} outlier month(s)","Commercial Director"))
    if not actions:         actions.append(("🟢 Good","All KPIs","Dashboard signals are healthy — continue monitoring","All"))

    action_df = pd.DataFrame(actions, columns=["Priority","Area","Recommended Action","Owner"])
    st.dataframe(
        action_df.style
        .map(lambda v: "color:#D13438;font-weight:700" if "Critical" in str(v)
             else ("color:#FF8C00;font-weight:700" if "Monitor" in str(v)
             else "color:#107C10;font-weight:700"), subset=["Priority"]),
        use_container_width=True,
        hide_index=True,
    )
