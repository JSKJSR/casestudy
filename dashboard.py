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
                ("Budget",       fmt(K["budget"]),          False, "#252423"),
                ("vs Budget",    f"{vs_bgt_arrow} {fmt(K['vs_bgt'],'%')}", True, vs_bgt_color),
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

    st.markdown('<p class="sec-lbl">Revenue Trend</p>', unsafe_allow_html=True)

    # ── Monthly Actual (by Store Channel) vs Budget vs LY ────────────────────
    sales_ch = sales.merge(store_raw[["Store ID","Store Channel"]], on="Store ID", how="left")

    ma_ch = (sales_ch.groupby(["Year","Month","Store Channel"])["Net Sales"].sum()
             .reset_index()
             .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1)))
             .sort_values("Date"))

    ma = (ma_ch.groupby("Date")["Net Sales"].sum().reset_index())

    mb = (budget.groupby(["Year","Month"])["Budget Sales"].sum().reset_index()
          .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1))))

    ly_yrs = [y-1 for y in sel_years]
    max_actual_date = ma["Date"].max()  # last month with real data
    ml = (sales_raw[sales_raw["Year"].isin(ly_yrs) &
                    sales_raw["Store ID"].isin(valid_stores) &
                    sales_raw["Product ID"].isin(valid_prods)]
          .groupby(["Year","Month"])["Net Sales"].sum().reset_index()
          .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1))
                                 + pd.DateOffset(years=1)))
    ml = ml[ml["Date"] <= max_actual_date]  # clip to actual data range

    # Outlier detection on total monthly net sales
    if len(ma) >= 4:
        q1, q3 = ma["Net Sales"].quantile([0.25, 0.75])
        iqr = q3 - q1
        _outliers = ma[(ma["Net Sales"] < q1 - 1.5*iqr) | (ma["Net Sales"] > q3 + 1.5*iqr)]
    else:
        _outliers = pd.DataFrame()

    channels      = sorted(ma_ch["Store Channel"].dropna().unique())
    ch_colors     = {"Full Price": C["blue"], "Outlet": C["teal"]}
    ch_color_list = [ch_colors.get(c, C["purple"]) for c in channels]

    fig = go.Figure()
    for ch, col in zip(channels, ch_color_list):
        ch_data = ma_ch[ma_ch["Store Channel"] == ch]
        fig.add_trace(go.Bar(
            x=ch_data["Date"], y=ch_data["Net Sales"],
            name=ch, marker_color=col, opacity=.85,
        ))
    fig.add_trace(go.Scatter(
        x=mb["Date"], y=mb["Budget Sales"],
        name="Budget", line=dict(color=C["amber"], width=2, dash="dash"),
    ))
    if not ml.empty:
        fig.add_trace(go.Scatter(
            x=ml["Date"], y=ml["Net Sales"],
            name="Prior Year", line=dict(color=C["grey"], width=1.5, dash="dot"),
        ))
    if not _outliers.empty:
        fig.add_trace(go.Scatter(
            x=_outliers["Date"], y=_outliers["Net Sales"],
            mode="markers+text", name="⚠ Outlier",
            marker=dict(color=C["red"], size=12, symbol="circle-open", line=dict(width=2)),
            text=_outliers["Net Sales"].apply(fmt), textposition="top center",
        ))
    fig.update_layout(
        title="Monthly Net Revenue by Store Channel · vs Budget vs Prior Year  (⚠ = outlier ±1.5 IQR)",
        height=340, barmode="stack",
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
                              name="Budget", marker_color=C["amber"], opacity=.45),
                       secondary_y=False)
        fig2.add_trace(go.Scatter(x=yy["Year"].astype(str), y=yy["vs%"],
                                  name="vs Bgt %", mode="lines+markers+text",
                                  text=yy["vs%"].apply(lambda v: fmt(v,"%")),
                                  textposition="top center",
                                  line=dict(color=C["red"], width=2)),
                       secondary_y=True)
        fig2.update_layout(title="Annual Actual vs Budget", barmode="group",
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

    # ── Country KPI strip ─────────────────────────────────────────────────────
    st.markdown('<p class="sec-lbl">Geography</p>', unsafe_allow_html=True)
    cnt = (sales.merge(store_raw[["Store ID","Store Country"]],on="Store ID",how="left")
           .groupby("Store Country")["Net Sales"].sum().reset_index()
           .sort_values("Net Sales", ascending=False))
    cnt["share"] = cnt["Net Sales"] / cnt["Net Sales"].sum() * 100
    for col, (_, row) in zip(st.columns(len(cnt)), cnt.iterrows()):
        col.metric(row["Store Country"], fmt(row["Net Sales"]),
                   f"{row['share']:.0f}% of total")


# ══════════════════════════════════════════════════════════════════════════════
# ██  PAGE 2 — SALES PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Sales Performance":

    st.markdown('<p class="pg-title">Sales Performance</p>', unsafe_allow_html=True)
    st.markdown('<p class="pg-sub">Time intelligence · Budget variance · Returns · Discounts</p>', unsafe_allow_html=True)

    K2   = calc_kpis(sales, budget)
    ly2  = ly_net_sales()
    vs_ly2 = (K2["net_sales"] / ly2 - 1) * 100 if ly2 else 0
    avg_d  = sales[sales["Order Type"]=="Sales"]["Discount"].mean() * 100

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.metric("Net Sales",      fmt(K2["net_sales"]))
    k2.metric("Gross Profit",   fmt(K2["gross_profit"]))
    k3.metric("Profit Margin",  f"{K2['profit_margin']:.1f}%")
    k4.metric("vs Budget",      fmt(K2["vs_bgt"],"%"))
    k5.metric("vs LY",          fmt(vs_ly2,"%"))
    k6.metric("Avg Discount",   f"{avg_d:.1f}%")

    st.markdown('<p class="sec-lbl">Monthly Budget Variance</p>', unsafe_allow_html=True)

    ma2 = (sales.groupby(["Year","Month"])["Net Sales"].sum().reset_index()
           .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1))))
    mb2 = (budget.groupby(["Year","Month"])["Budget Sales"].sum().reset_index()
           .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1))))
    mrg = ma2.merge(mb2, on="Date", how="outer").sort_values("Date")
    mrg["Var"]  = mrg["Net Sales"] - mrg["Budget Sales"]
    mrg["Var%"] = (mrg["Net Sales"] / mrg["Budget Sales"] - 1) * 100
    mrg["Col"]  = mrg["Var"].apply(lambda v: C["green"] if v >= 0 else C["red"])

    fig_v = go.Figure()
    fig_v.add_trace(go.Bar(x=mrg["Date"], y=mrg["Var"],
                           marker_color=mrg["Col"], name="$ Variance", opacity=.85))
    fig_v.add_trace(go.Scatter(x=mrg["Date"], y=mrg["Var%"],
                               name="% Variance", yaxis="y2",
                               line=dict(color=C["navy"], width=1.5)))
    fig_v.add_hline(y=0, line_color="#374151", line_width=1)
    fig_v.update_layout(
        title="Monthly Revenue Variance vs Budget  (bar = $, line = %)",
        height=290,
        yaxis=dict(title="$ Variance", showgrid=True, gridcolor=C["grid"], tickprefix="$"),
        yaxis2=dict(title="% Variance", overlaying="y", side="right",
                    ticksuffix="%", showgrid=False),
        legend=dict(orientation="h", y=-0.22), **CHART)
    st.plotly_chart(fig_v, use_container_width=True)

    col_yoy, col_roll = st.columns(2)

    with col_yoy:
        fall = (sales_raw[sales_raw["Store ID"].isin(valid_stores) &
                          sales_raw["Product ID"].isin(valid_prods)]
                .groupby(["Year","Month"])["Net Sales"].sum().reset_index()
                .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1)))
                .sort_values("Date"))
        fall["YoY%"] = fall.groupby("Month")["Net Sales"].pct_change() * 100
        yoy = fall[fall["Year"].isin(sel_years)].dropna(subset=["YoY%"]).copy()
        yoy["C"] = yoy["YoY%"].apply(lambda v: C["green"] if v >= 0 else C["red"])
        fig_yoy = go.Figure(go.Bar(x=yoy["Date"], y=yoy["YoY%"],
                                   marker_color=yoy["C"], opacity=.85))
        fig_yoy.add_hline(y=0, line_color="#374151", line_width=1)
        fig_yoy.update_layout(title="YoY Growth % (month-over-month)", height=260,
                              yaxis=dict(showgrid=True, gridcolor=C["grid"], ticksuffix="%"),
                              **CHART)
        st.plotly_chart(fig_yoy, use_container_width=True)

    with col_roll:
        fall["Roll3"]  = fall["Net Sales"].rolling(3,  min_periods=1).mean()
        fall["Roll12"] = fall["Net Sales"].rolling(12, min_periods=1).mean()
        vis = fall[fall["Year"].isin(sel_years)]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatter(x=vis["Date"], y=vis["Net Sales"],
                                   name="Monthly", opacity=.35,
                                   line=dict(color=C["blue"], width=1)))
        fig_r.add_trace(go.Scatter(x=vis["Date"], y=vis["Roll3"],
                                   name="3M Avg", line=dict(color=C["amber"], width=2)))
        fig_r.add_trace(go.Scatter(x=vis["Date"], y=vis["Roll12"],
                                   name="12M Avg",
                                   line=dict(color=C["green"], width=2, dash="dash")))
        fig_r.update_layout(title="Rolling Revenue Averages", height=260,
                            legend=dict(orientation="h", y=-0.28),
                            yaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="$"),
                            **CHART)
        st.plotly_chart(fig_r, use_container_width=True)

    st.markdown('<p class="sec-lbl">Returns</p>', unsafe_allow_html=True)
    ret_src = (sales_raw[sales_raw["Store ID"].isin(valid_stores) &
                         sales_raw["Year"].isin(sel_years)]
               .groupby(["Year","Month","Order Type"])["Sales"].sum()
               .reset_index()
               .pivot_table(index=["Year","Month"], columns="Order Type",
                            values="Sales", fill_value=0)
               .reset_index())

    cr1, cr2 = st.columns(2)
    if "Return" in ret_src.columns and "Sales" in ret_src.columns:
        ret_src["Ret%"] = ret_src["Return"] / ret_src["Sales"] * 100
        ret_src["Date"] = pd.to_datetime(ret_src[["Year","Month"]].assign(day=1))
        ret_src = ret_src.sort_values("Date")
        with cr1:
            fig_ret = px.area(ret_src, x="Date", y="Ret%",
                              title="Monthly Return Rate %",
                              color_discrete_sequence=[C["red"]])
            fig_ret.update_layout(height=230,
                                  yaxis=dict(showgrid=True, gridcolor=C["grid"],
                                             ticksuffix="%"), **CHART)
            st.plotly_chart(fig_ret, use_container_width=True)

    with cr2:
        ret_cat = (sales[sales["Order Type"]=="Return"]
                   .merge(product_raw[["Product ID","Category"]], on="Product ID", how="left")
                   .groupby("Category")["Sales"].sum().reset_index()
                   .sort_values("Sales", ascending=False))
        ret_cat["lbl"] = ret_cat["Sales"].apply(fmt)
        fig_rc = go.Figure(go.Bar(x=ret_cat["Category"], y=ret_cat["Sales"],
                                  text=ret_cat["lbl"], textposition="outside",
                                  marker_color=C["red"], opacity=.8))
        fig_rc.update_layout(title="Return Value by Category", height=230,
                             yaxis=dict(showgrid=True, gridcolor=C["grid"],
                                        tickprefix="$"), **CHART)
        st.plotly_chart(fig_rc, use_container_width=True)

    st.markdown('<p class="sec-lbl">Discount Impact</p>', unsafe_allow_html=True)
    tmp = sales.copy()
    tmp["Band"] = pd.cut(tmp["Discount"],
                         bins=[-0.001,0,.10,.20,.30,.50,1.],
                         labels=["0%","1–10%","11–20%","21–30%","31–50%",">50%"])
    disc = (tmp.groupby("Band", observed=True)
            .agg(Revenue=("Net Sales","sum"), Txn=("Order ID","count"))
            .reset_index())
    disc["lbl"] = disc["Revenue"].apply(fmt)

    dd1, dd2 = st.columns(2)
    with dd1:
        fig_d1 = go.Figure(go.Bar(x=disc["Band"], y=disc["Revenue"],
                                  text=disc["lbl"], textposition="outside",
                                  marker_color=C["blue"]))
        fig_d1.update_layout(title="Revenue by Discount Band", height=230,
                             yaxis=dict(showgrid=True, gridcolor=C["grid"],
                                        tickprefix="$"), **CHART)
        st.plotly_chart(fig_d1, use_container_width=True)
    with dd2:
        fig_d2 = go.Figure(go.Bar(x=disc["Band"], y=disc["Txn"],
                                  text=disc["Txn"], textposition="outside",
                                  marker_color=C["teal"]))
        fig_d2.update_layout(title="Transaction Count by Discount Band", height=230,
                             yaxis=dict(showgrid=True, gridcolor=C["grid"]), **CHART)
        st.plotly_chart(fig_d2, use_container_width=True)


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
    st.markdown('<p class="pg-sub">Per-store KPIs · Efficiency · LFL · Area managers</p>', unsafe_allow_html=True)

    # Per-store KPIs using correct split: sales rows for COGS/orders, return rows for return metrics
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

    st_agg["ReturnSales"]  = st_agg["ReturnSales"].fillna(0)
    st_agg["ReturnCost"]   = st_agg["ReturnCost"].fillna(0)

    # KPI 3 – Net Sales
    st_agg["Revenue"]      = st_agg["GrossSales"] - st_agg["ReturnSales"].abs()
    # KPI 6 – Net COGS
    st_agg["NetCOGS"]      = st_agg["COGS"] - st_agg["ReturnCost"].abs()
    # KPI 7 – Gross Profit
    st_agg["GrossProfit"]  = st_agg["Revenue"] - st_agg["NetCOGS"]
    # KPI 8 – Profit Margin
    st_agg["GM%"]          = (st_agg["GrossProfit"] / st_agg["Revenue"] * 100).fillna(0)
    # KPI 10 – AOV (÷ sales orders only)
    st_agg["AOV"]          = st_agg["Revenue"] / st_agg["SalesOrders"]
    # KPI 11 – Units per Order (sales qty ÷ sales orders)
    st_agg["Units/Order"]  = st_agg["SalesQty"] / st_agg["SalesOrders"]
    # KPI 12 – Return Rate
    st_agg["ReturnRate%"]  = (st_agg["ReturnSales"].abs() / st_agg["GrossSales"] * 100).fillna(0)
    # Store efficiency
    st_agg["Sales/SQM"]    = st_agg["Revenue"] / st_agg["Store SQM"]
    st_agg["vs Bgt%"]      = (st_agg["Revenue"] / st_agg["Budget Sales"] - 1) * 100

    # Network-level KPIs via calc_kpis()
    KS = calc_kpis(sales, budget)

    k1,k2,k3,k4,k5,k6,k7 = st.columns(7)
    k1.metric("Total Stores",   f"{st_agg['Store ID'].nunique()}")
    k2.metric("Open Stores",    f"{(st_agg['Store Status']=='Open').sum()}")
    k3.metric("Net Sales",      fmt(KS["net_sales"]))
    k4.metric("Gross Profit",   fmt(KS["gross_profit"]))
    k5.metric("Profit Margin",  f"{KS['profit_margin']:.1f}%")
    k6.metric("Avg AOV",        f"${st_agg['AOV'].mean():.0f}")
    k7.metric("Avg $/SQM",      f"${st_agg['Sales/SQM'].mean():.0f}")

    st.markdown('<p class="sec-lbl">Store vs Budget</p>', unsafe_allow_html=True)
    cs1, cs2 = st.columns([3,2])

    with cs1:
        top = st_agg.sort_values("Revenue", ascending=True).tail(20)
        fig_sb = go.Figure()
        fig_sb.add_trace(go.Bar(y=top["Store Name"], x=top["Revenue"],
                                name="Actual", orientation="h",
                                marker_color=C["blue"]))
        fig_sb.add_trace(go.Bar(y=top["Store Name"], x=top["Budget Sales"],
                                name="Budget", orientation="h",
                                marker_color=C["amber"], opacity=.4))
        fig_sb.update_layout(
            title="Store Revenue: Actual vs Budget",
            barmode="overlay", height=500,
            legend=dict(orientation="h", y=-0.08),
            xaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="$"),
            **CHART)
        st.plotly_chart(fig_sb, use_container_width=True)

    with cs2:
        fig_sc = px.scatter(
            st_agg, x="Sales/SQM", y="vs Bgt%",
            size="Revenue", color="Store Country",
            hover_name="Store Name",
            title="Efficiency · $/SQM vs vs Budget %",
            size_max=42,
            color_discrete_sequence=[C["blue"],C["amber"],C["green"],C["purple"]],
        )
        fig_sc.add_hline(y=0, line_dash="dash", line_color=C["red"], opacity=.5)
        fig_sc.add_vline(x=st_agg["Sales/SQM"].median(),
                         line_dash="dot", line_color=C["grey"], opacity=.4)
        fig_sc.update_layout(
            height=500,
            xaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="$"),
            yaxis=dict(showgrid=True, gridcolor=C["grid"], ticksuffix="%"),
            **CHART)
        st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown('<p class="sec-lbl">Like-for-Like (LFL)</p>', unsafe_allow_html=True)
    lfl_ids  = st_agg.loc[st_agg["Store LFL Status"]==1,"Store ID"].tolist()
    lfl_rev  = st_agg.loc[st_agg["Store LFL Status"]==1,"Revenue"].sum()
    tot_rev  = st_agg["Revenue"].sum()

    la,lb,lc_ = st.columns(3)
    la.metric("LFL Stores",    f"{len(lfl_ids)}")
    lb.metric("LFL Revenue",   fmt(lfl_rev))
    lc_.metric("LFL % of Total",f"{lfl_rev/tot_rev*100:.1f}%" if tot_rev else "N/A")

    mall = (sales.groupby(["Year","Month"])["Net Sales"].sum().reset_index()
            .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1)))
            .sort_values("Date"))
    mlfl = (sales[sales["Store ID"].isin(lfl_ids)]
            .groupby(["Year","Month"])["Net Sales"].sum().reset_index()
            .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1)))
            .sort_values("Date"))
    fig_lfl = go.Figure()
    fig_lfl.add_trace(go.Scatter(x=mall["Date"], y=mall["Net Sales"],
                                 name="All Stores",
                                 line=dict(color=C["blue"], width=2)))
    fig_lfl.add_trace(go.Scatter(x=mlfl["Date"], y=mlfl["Net Sales"],
                                 name="LFL Stores",
                                 line=dict(color=C["green"], width=2, dash="dash")))
    fig_lfl.update_layout(title="LFL vs Total Network – Monthly Revenue",
                          height=230, legend=dict(orientation="h",y=-0.25),
                          xaxis=dict(showgrid=False),
                          yaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="$"),
                          **CHART)
    st.plotly_chart(fig_lfl, use_container_width=True)

    st.markdown('<p class="sec-lbl">Management View</p>', unsafe_allow_html=True)
    ma1, ma2 = st.columns(2)

    with ma1:
        am = (st_agg.groupby("Store Area Manager")
              .agg(Revenue=("Revenue","sum")).reset_index()
              .sort_values("Revenue", ascending=False))
        am["lbl"] = am["Revenue"].apply(fmt)
        fig_am = go.Figure(go.Bar(x=am["Store Area Manager"], y=am["Revenue"],
                                  text=am["lbl"], textposition="outside",
                                  marker_color=C["navy"]))
        fig_am.update_layout(title="Revenue by Area Manager", height=260,
                             yaxis=dict(showgrid=True, gridcolor=C["grid"],
                                        tickprefix="$"), **CHART)
        st.plotly_chart(fig_am, use_container_width=True)

    with ma2:
        fmt_a = st_agg.groupby("Store Format")["Revenue"].sum().reset_index()
        fig_f = px.pie(fmt_a, values="Revenue", names="Store Format",
                       title="Revenue by Store Format", hole=.45,
                       color_discrete_sequence=[C["blue"],C["teal"],C["amber"]])
        fig_f.update_layout(height=260, **CHART)
        st.plotly_chart(fig_f, use_container_width=True)

    st.markdown('<p class="sec-lbl">Store Detail</p>', unsafe_allow_html=True)
    tbl = st_agg[["Store Name","Store Country","Store Channel","Store Format",
                  "Store Status","GrossSales","Revenue","Budget Sales",
                  "vs Bgt%","GrossProfit","GM%","ReturnRate%",
                  "AOV","Units/Order","Sales/SQM"]].copy()
    tbl.columns = ["Store","Country","Channel","Format","Status",
                   "Gross Sales","Net Sales","Budget","vs Bgt%",
                   "Gross Profit","GM%","Return Rate%","AOV","Units/Order","$/SQM"]
    st.dataframe(
        tbl.style
        .format({"Gross Sales":"${:,.0f}","Net Sales":"${:,.0f}",
                 "Budget":"${:,.0f}","vs Bgt%":"{:+.1f}%",
                 "Gross Profit":"${:,.0f}","GM%":"{:.1f}%",
                 "Return Rate%":"{:.1f}%","AOV":"${:.0f}",
                 "Units/Order":"{:.2f}","$/SQM":"${:.0f}"})
        .background_gradient(subset=["Net Sales"], cmap="Blues")
        .map(lambda v: "color:#107C10;font-weight:700" if isinstance(v,(int,float)) and v>=0
             else ("color:#D13438;font-weight:700" if isinstance(v,(int,float)) else ""),
             subset=["vs Bgt%"]),
        use_container_width=True,
        hide_index=True,
    )

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
    if vs_b < -10:          actions.append(("🔴 Critical","Revenue vs Budget","Activate recovery plan: pricing, promotions, store reviews","CFO / Commercial Director"))
    elif vs_b < 0:          actions.append(("🟡 Monitor","Revenue vs Budget","Weekly budget variance review with area managers","Commercial Director"))
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
