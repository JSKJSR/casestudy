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
# SYNTHETIC DATA GENERATION  (mirrors the real Intersport dataset structure)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⏳ Building dataset…")
def generate_data():
    rng = np.random.default_rng(42)

    # ── Store master ──────────────────────────────────────────────────────────
    store_info = [
        ("LD-01","Store 1","Full Price","Flagship","UK","United Kingdom","London",820,"J. Brown","2018-05-01",1,"2019-05-01","Open"),
        ("LD-02","Store 2","Full Price","Flagship","NL","The Netherlands","Amsterdam",640,"M. de Vries","2019-03-15",1,"2020-03-15","Open"),
        ("LD-03","Store 3","Full Price","Concession","NL","The Netherlands","Rotterdam",580,"M. de Vries","2020-09-01",1,"2021-09-01","Open"),
        ("LD-04","Store 4","Outlet","Concession","UK","United Kingdom","Manchester",420,"J. Brown","2017-11-01",1,"2018-11-01","Open"),
        ("LD-05","Store 5","Full Price","Flagship","DE","Germany","Berlin",900,"T. Weber","2018-06-01",1,"2019-06-01","Open"),
        ("LD-06","Store 6","Full Price","Concession","DE","Germany","Munich",520,"T. Weber","2019-08-01",1,"2020-08-01","Open"),
        ("LD-07","Store 7","Outlet","Pop-Up","FR","France","Paris",350,"C. Dubois","2020-03-01",1,"2021-03-01","Open"),
        ("LD-08","Store 8","Full Price","Flagship","UK","United Kingdom","London",780,"J. Brown","2017-04-01",1,"2018-04-01","Open"),
        ("LD-09","Store 9","Full Price","Concession","NL","The Netherlands","Utrecht",460,"L. Bakker","2021-01-15",1,"2022-01-15","Open"),
        ("LD-10","Store 10","Outlet","Pop-Up","DE","Germany","Hamburg",310,"K. Fischer","2021-06-01",0,"2023-06-01","Open"),
        ("LD-11","Store 11","Full Price","Concession","FR","France","Lyon",490,"P. Laurent","2019-12-01",1,"2020-12-01","Open"),
        ("LD-12","Store 12","Full Price","Flagship","UK","United Kingdom","Birmingham",720,"R. Smith","2018-09-01",1,"2019-09-01","Open"),
        ("LD-13","Store 13","Outlet","Concession","DE","Germany","Cologne",380,"T. Weber","2020-04-01",0,"2022-04-01","Open"),
        ("LD-14","Store 14","Full Price","Concession","FR","France","Marseille",430,"C. Dubois","2021-07-01",0,"2023-07-01","Open"),
        ("LD-15","Store 15","Full Price","Flagship","NL","The Netherlands","Amsterdam",860,"M. de Vries","2016-10-01",1,"2017-10-01","Open"),
        ("LD-16","Store 16","Outlet","Pop-Up","UK","United Kingdom","Leeds",290,"J. Brown","2022-02-01",0,"2024-02-01","Open"),
        ("LD-17","Store 17","Full Price","Concession","DE","Germany","Frankfurt",540,"K. Fischer","2019-05-01",1,"2020-05-01","Open"),
        ("LD-18","Store 18","Full Price","Flagship","FR","France","Paris",980,"P. Laurent","2017-03-01",1,"2018-03-01","Open"),
        ("LD-19","Store 19","Outlet","Concession","UK","United Kingdom","Glasgow",360,"R. Smith","2020-11-01",0,"2022-11-01","Open"),
        ("LD-20","Store 20","Full Price","Concession","NL","The Netherlands","Rotterdam",410,"L. Bakker","2021-09-01",0,"2023-09-01","Open"),
        ("LD-21","Store 21","Full Price","Flagship","DE","Germany","Berlin",760,"T. Weber","2018-01-01",1,"2019-01-01","Open"),
        ("LD-22","Store 22","Outlet","Pop-Up","FR","France","Nice",280,"C. Dubois","2022-05-01",0,"2024-05-01","Open"),
        ("LD-23","Store 23","Full Price","Concession","UK","United Kingdom","Bristol",500,"J. Brown","2019-07-01",1,"2020-07-01","Open"),
        ("LD-24","Store 24","Full Price","Flagship","NL","The Netherlands","The Hague",670,"M. de Vries","2018-08-01",1,"2019-08-01","Open"),
        ("LD-25","Store 25","Full Price","Concession","DE","Germany","Stuttgart",445,"K. Fischer","2020-06-01",1,"2021-06-01","Open"),
        ("LD-26","Store 26","Outlet","Concession","FR","France","Bordeaux",330,"P. Laurent","2021-04-01",0,"2023-04-01","Closed"),
        ("LD-27","Store 27","Full Price","Pop-Up","UK","United Kingdom","Edinburgh",260,"R. Smith","2022-09-01",0,"2024-09-01","Open"),
    ]
    store_cols = ["Store ID","Store Name","Store Channel","Store Format",
                  "Store Country Code","Store Country","Store City","Store SQM",
                  "Store Area Manager","Store Opening Date","Store LFL Status",
                  "Store LFL Date","Store Status"]
    store = pd.DataFrame(store_info, columns=store_cols)
    store["Store Opening Date"] = pd.to_datetime(store["Store Opening Date"])
    store["Store LFL Date"]     = pd.to_datetime(store["Store LFL Date"])

    # ── Product master ────────────────────────────────────────────────────────
    categories = {
        "Apparel":      (["Jackets","Tops","Bottoms","Footwear","Accessories"],        [85,45,60,120,35]),
        "Equipment":    (["Rackets","Balls","Fitness","Outdoor","Bikes"],               [150,40,90,200,600]),
        "Teamwear":     (["Jerseys","Shorts","Socks","Training Kits","Goalkeeper"],     [65,30,15,120,55]),
    }
    brands    = ["Nike","Adidas","Puma","Under Armour","Intersport","New Balance","Asics","Reebok"]
    tiers     = ["Good","Better","Best"]
    lifecycle = ["Running","Novelty","Bargain","Not assigned"]
    colours   = ["Black","White","Blue","Red","Green","Grey","Navy","Yellow"]
    materials = ["Polyester","Cotton","Leather","Rubber","Nylon","Mesh","Fleece"]

    prod_rows = []
    pid = 1
    for cat, (subcats, base_prices) in categories.items():
        for sub, bp in zip(subcats, base_prices):
            n = rng.integers(180, 260)
            for _ in range(n):
                unit = round(bp * rng.uniform(0.6, 2.2), 2)
                prod_rows.append({
                    "Product ID":  f"P{pid:04d}",
                    "Category":    cat,
                    "Sub-Category":sub,
                    "Product Name":f"Product {pid:04d}",
                    "Brand":       rng.choice(brands),
                    "Price Tier":  rng.choice(tiers, p=[0.45,0.35,0.20]),
                    "Lifecycle":   rng.choice(lifecycle, p=[0.55,0.20,0.15,0.10]),
                    "Unit Price":  unit,
                    "Cost Price":  round(unit * rng.uniform(0.45, 0.65), 2),
                    "Colour":      rng.choice(colours),
                    "Material":    rng.choice(materials),
                    "MOQ":         int(rng.integers(5, 200)),
                    "Product Image URL": "https://via.placeholder.com/80x80?text=IMG",
                })
                pid += 1
    product = pd.DataFrame(prod_rows)

    # ── Customers ─────────────────────────────────────────────────────────────
    segments = ["Consumer","Corporate","Home Office","Small Business"]
    genders  = ["Male","Female"]
    cities_by_country = {
        "United Kingdom": ["London","Manchester","Birmingham","Leeds","Glasgow","Bristol","Edinburgh"],
        "The Netherlands":["Amsterdam","Rotterdam","Utrecht","The Hague","Eindhoven"],
        "Germany":        ["Berlin","Munich","Hamburg","Cologne","Frankfurt","Stuttgart"],
        "France":         ["Paris","Lyon","Marseille","Nice","Bordeaux","Toulouse"],
    }
    cust_rows = []
    for i in range(17_000):
        country = rng.choice(list(cities_by_country))
        city    = rng.choice(cities_by_country[country])
        age     = int(rng.integers(18, 72))
        lo, hi  = (age // 5) * 5, (age // 5) * 5 + 4
        cust_rows.append({
            "Customer ID":           f"C{i+1:06d}",
            "Customer Name":         f"Customer {i+1}",
            "Customer Segment":      rng.choice(segments, p=[0.50,0.25,0.15,0.10]),
            "Customer Age":          age,
            "Customer Age Bucket":   f"{lo}-{hi}",
            "Customer Gender":       rng.choice(genders),
            "Customer City":         city,
            "Customer Country":      country,
            "Loyalty Member":        rng.choice(["Yes","No"], p=[0.35,0.65]),
        })
    customer = pd.DataFrame(cust_rows)

    # ── Sales Orders ──────────────────────────────────────────────────────────
    store_ids   = store["Store ID"].tolist()
    product_ids = product["Product ID"].tolist()
    customer_ids= customer["Customer ID"].tolist()

    dates = pd.date_range("2022-01-01", "2025-08-24", freq="D")
    n_orders = 44_000
    order_dates = rng.choice(dates, size=n_orders)

    # seasonal weight: Q4 gets ~40% more volume
    def seasonal_qty(month):
        return rng.integers(1, 6) * (1.4 if month in [10,11,12] else 1)

    sales_rows = []
    for i in range(n_orders):
        d        = pd.Timestamp(order_dates[i])
        prod_row = product.iloc[rng.integers(len(product))]
        qty      = max(1, int(seasonal_qty(d.month)))
        discount = float(rng.choice([0,0,0,0.05,0.10,0.15,0.20,0.25,0.30],
                                    p=[0.40,0.10,0.10,0.10,0.10,0.07,0.06,0.04,0.03]))
        unit     = prod_row["Unit Price"]
        sales_val= round(unit * qty * (1 - discount), 3)
        cost_val = round(prod_row["Cost Price"] * qty, 3)
        otype    = "Return" if rng.random() < 0.12 else "Sales"
        ship_d   = d + pd.Timedelta(days=int(rng.integers(1, 6)))
        inv_d    = d + pd.Timedelta(days=int(rng.integers(7, 15)))
        sales_rows.append({
            "Order Date":    d,
            "Order ID":      f"ORD-{i+1:06d}",
            "Customer ID":   customer_ids[rng.integers(len(customer_ids))],
            "Store ID":      store_ids[rng.integers(len(store_ids))],
            "Product ID":    prod_row["Product ID"],
            "Order Type":    otype,
            "Quantity":      qty,
            "Cost":          cost_val,
            "Discount":      discount,
            "Sales":         sales_val,
            "Shipping Date": ship_d,
            "Invoice Date":  inv_d,
        })
    sales = pd.DataFrame(sales_rows)

    # ── Budget  (monthly, per store, ~95% of rolling actual average) ──────────
    bgt_rows = []
    for sid in store_ids:
        for yr in [2022, 2023, 2024, 2025]:
            months = range(1, 9) if yr == 2025 else range(1, 13)
            for mo in months:
                bgt_rows.append({
                    "Budget Date":     pd.Timestamp(f"{yr}-{mo:02d}-01"),
                    "Store ID":        sid,
                    "Budget Sales":    int(rng.integers(18_000, 52_000)),
                    "Budget Quantity": int(rng.integers(300, 900)),
                })
    budget = pd.DataFrame(bgt_rows)
    budget["Year"]  = budget["Budget Date"].dt.year
    budget["Month"] = budget["Budget Date"].dt.month

    # ── Enrich sales ──────────────────────────────────────────────────────────
    sales["Year"]    = sales["Order Date"].dt.year
    sales["Month"]   = sales["Order Date"].dt.month
    sales["Quarter"] = "Q" + sales["Order Date"].dt.quarter.astype(str)
    sign = sales["Order Type"].map({"Sales": 1, "Return": -1})
    sales["Net Sales"] = sales["Sales"]    * sign
    sales["Net Cost"]  = sales["Cost"]     * sign
    sales["Net Qty"]   = sales["Quantity"] * sign

    return dict(sales=sales, budget=budget, store=store,
                product=product, customer=customer)


# load once
_t0 = time.perf_counter()
DATA = generate_data()
_load_ms = (time.perf_counter() - _t0) * 1000

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def fmt(v, mode="€"):
    if mode == "€":
        if abs(v) >= 1_000_000: return f"€{v/1_000_000:.2f}M"
        if abs(v) >= 1_000:     return f"€{v/1_000:.1f}K"
        return f"€{v:,.0f}"
    s = "+" if v >= 0 else ""
    return f"{s}{v:.1f}%"


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

    # ── KPIs ──────────────────────────────────────────────────────────────────
    net_s  = sales["Net Sales"].sum()
    net_c  = sales["Net Cost"].sum()
    net_q  = int(sales["Net Qty"].sum())
    gm     = (net_s - net_c) / net_s * 100 if net_s else 0
    tot_b  = budget["Budget Sales"].sum()
    vs_b   = (net_s / tot_b - 1) * 100 if tot_b else 0
    ly     = ly_net_sales()
    vs_ly  = (net_s / ly - 1) * 100 if ly else 0
    gross  = sales.loc[sales["Order Type"]=="Sales","Sales"].sum()
    ret    = sales.loc[sales["Order Type"]=="Return","Sales"].sum()
    ret_rt = ret / gross * 100 if gross else 0

    # YTD: use months 1–latest month in selected period
    max_month = sales["Month"].max() if not sales.empty else 12
    ytd_sales  = sales[sales["Month"] <= max_month]["Net Sales"].sum()
    ly_yrs_ytd = [y - 1 for y in sel_years]
    ytd_ly     = sales_raw[
        sales_raw["Year"].isin(ly_yrs_ytd) &
        sales_raw["Store ID"].isin(valid_stores) &
        sales_raw["Product ID"].isin(valid_prods) &
        (sales_raw["Month"] <= max_month)
    ]["Net Sales"].sum()
    ytd_bgt    = budget[budget["Month"] <= max_month]["Budget Sales"].sum()
    vs_ytd_ly  = (ytd_sales / ytd_ly - 1) * 100 if ytd_ly else 0
    vs_ytd_bgt = (ytd_sales / ytd_bgt - 1) * 100 if ytd_bgt else 0

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Net Revenue",   fmt(net_s),
              delta=f"{fmt(vs_ly,'%')} vs LY",
              delta_color="normal" if vs_ly >= 0 else "inverse")
    c2.metric("vs Budget",     fmt(vs_b,"%"),
              delta=fmt(net_s - tot_b),
              delta_color="normal" if vs_b >= 0 else "inverse")
    c3.metric("Gross Margin",  f"{gm:.1f}%")
    c4.metric("Units Sold",    f"{net_q:,}")
    c5.metric("LY Revenue",    fmt(ly))
    c6.metric("Return Rate",   f"{ret_rt:.1f}%",
              delta_color="inverse")

    # ── YTD strip ─────────────────────────────────────────────────────────────
    st.markdown('<p class="sec-lbl">YTD Time Intelligence (Jan → latest month in selection)</p>',
                unsafe_allow_html=True)
    y1,y2,y3 = st.columns(3)
    y1.metric(f"YTD Revenue (M{max_month:02d})", fmt(ytd_sales),
              delta=f"{fmt(vs_ytd_ly,'%')} vs LY YTD",
              delta_color="normal" if vs_ytd_ly >= 0 else "inverse")
    y2.metric("YTD vs Budget",  fmt(vs_ytd_bgt,"%"),
              delta=fmt(ytd_sales - ytd_bgt),
              delta_color="normal" if vs_ytd_bgt >= 0 else "inverse")
    y3.metric("YTD LY",        fmt(ytd_ly))

    st.markdown('<p class="sec-lbl">Revenue Trend</p>', unsafe_allow_html=True)

    # ── Monthly Actual vs Budget vs LY ────────────────────────────────────────
    ma = (sales.groupby(["Year","Month"])["Net Sales"].sum().reset_index()
          .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1)))
          .sort_values("Date"))
    mb = (budget.groupby(["Year","Month"])["Budget Sales"].sum().reset_index()
          .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1))))
    ly_yrs = [y-1 for y in sel_years]
    ml = (sales_raw[sales_raw["Year"].isin(ly_yrs) &
                    sales_raw["Store ID"].isin(valid_stores) &
                    sales_raw["Product ID"].isin(valid_prods)]
          .groupby(["Year","Month"])["Net Sales"].sum().reset_index()
          .assign(Date=lambda d: pd.to_datetime(d[["Year","Month"]].assign(day=1))
                                 + pd.DateOffset(years=1)))

    # Outlier detection: flag months > 1.5 IQR from Q1/Q3
    if len(ma) >= 4:
        q1, q3 = ma["Net Sales"].quantile([0.25, 0.75])
        iqr = q3 - q1
        _outliers = ma[(ma["Net Sales"] < q1 - 1.5*iqr) | (ma["Net Sales"] > q3 + 1.5*iqr)]
    else:
        _outliers = pd.DataFrame()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=ma["Date"], y=ma["Net Sales"],
                         name="Actual", marker_color=C["blue"], opacity=.85))
    fig.add_trace(go.Scatter(x=mb["Date"], y=mb["Budget Sales"],
                             name="Budget",
                             line=dict(color=C["amber"], width=2, dash="dash")))
    if not ml.empty:
        fig.add_trace(go.Scatter(x=ml["Date"], y=ml["Net Sales"],
                                 name="Prior Year",
                                 line=dict(color=C["grey"], width=1.5, dash="dot")))
    if not _outliers.empty:
        fig.add_trace(go.Scatter(
            x=_outliers["Date"], y=_outliers["Net Sales"],
            mode="markers+text",
            name="⚠ Outlier",
            marker=dict(color=C["red"], size=12, symbol="circle-open", line=dict(width=2)),
            text=_outliers["Net Sales"].apply(fmt),
            textposition="top center",
        ))
    fig.update_layout(title="Monthly Net Revenue · Actual vs Budget vs Prior Year  (⚠ = statistical outlier ±1.5 IQR)",
                      height=320, barmode="overlay",
                      legend=dict(orientation="h", y=-0.22),
                      xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="€"),
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
        fig2.update_yaxes(tickprefix="€", secondary_y=False,
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
                           yaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="€"),
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

    net_s  = sales["Net Sales"].sum()
    net_c  = sales["Net Cost"].sum()
    gm     = (net_s - net_c) / net_s * 100 if net_s else 0
    tot_b  = budget["Budget Sales"].sum()
    vs_b   = (net_s / tot_b - 1) * 100 if tot_b else 0
    ly     = ly_net_sales()
    vs_ly  = (net_s / ly - 1) * 100 if ly else 0
    avg_d  = sales["Discount"].mean() * 100

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("Net Revenue",  fmt(net_s))
    k2.metric("Gross Margin", f"{gm:.1f}%")
    k3.metric("vs Budget",    fmt(vs_b,"%"))
    k4.metric("vs LY",        fmt(vs_ly,"%"))
    k5.metric("Avg Discount", f"{avg_d:.1f}%")

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
                           marker_color=mrg["Col"], name="€ Variance", opacity=.85))
    fig_v.add_trace(go.Scatter(x=mrg["Date"], y=mrg["Var%"],
                               name="% Variance", yaxis="y2",
                               line=dict(color=C["navy"], width=1.5)))
    fig_v.add_hline(y=0, line_color="#374151", line_width=1)
    fig_v.update_layout(
        title="Monthly Revenue Variance vs Budget  (bar = €, line = %)",
        height=290,
        yaxis=dict(title="€ Variance", showgrid=True, gridcolor=C["grid"], tickprefix="€"),
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
                            yaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="€"),
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
                                        tickprefix="€"), **CHART)
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
                                        tickprefix="€"), **CHART)
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

    net_s = ps["Net Sales"].sum()
    net_c = ps["Net Cost"].sum()
    gm    = (net_s - net_c) / net_s * 100 if net_s else 0
    prods = ps["Product ID"].nunique()
    avg_d = ps["Discount"].mean() * 100

    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total Revenue",    fmt(net_s))
    k2.metric("Gross Margin",     f"{gm:.1f}%")
    k3.metric("Unique SKUs Sold", f"{prods:,}")
    k4.metric("Avg Discount",     f"{avg_d:.1f}%")

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
            xaxis=dict(title="Revenue (€)", showgrid=True, gridcolor=C["grid"]),
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
                                        tickprefix="€"), **CHART)
        st.plotly_chart(fig_lc, use_container_width=True)

    with pm3:
        br = (ps.groupby("Brand")["Net Sales"].sum().reset_index()
              .sort_values("Net Sales", ascending=False).head(8)
              .sort_values("Net Sales"))
        fig_br = go.Figure(go.Bar(y=br["Brand"], x=br["Net Sales"],
                                  orientation="h", marker_color=C["purple"]))
        fig_br.update_layout(title="Top 8 Brands", height=240,
                             xaxis=dict(showgrid=True, gridcolor=C["grid"],
                                        tickprefix="€"), **CHART)
        st.plotly_chart(fig_br, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ██  PAGE 4 — STORE NETWORK
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Store Network":

    st.markdown('<p class="pg-title">Store Network</p>', unsafe_allow_html=True)
    st.markdown('<p class="pg-sub">Per-store KPIs · Efficiency · LFL · Area managers</p>', unsafe_allow_html=True)

    bgt_s  = budget.groupby("Store ID")["Budget Sales"].sum().reset_index()
    st_agg = (sales.groupby("Store ID")
              .agg(Revenue=("Net Sales","sum"), Cost=("Net Cost","sum"),
                   Qty=("Net Qty","sum"), Txn=("Order ID","nunique"))
              .reset_index()
              .merge(store_raw[["Store ID","Store Name","Store Country",
                                "Store Channel","Store Format","Store SQM",
                                "Store Area Manager","Store LFL Status",
                                "Store Status"]], on="Store ID", how="left")
              .merge(bgt_s, on="Store ID", how="left"))

    st_agg["GM%"]       = (st_agg["Revenue"]-st_agg["Cost"])/st_agg["Revenue"]*100
    st_agg["Sales/SQM"] = st_agg["Revenue"]/st_agg["Store SQM"]
    st_agg["vs Bgt%"]   = (st_agg["Revenue"]/st_agg["Budget Sales"]-1)*100
    st_agg["Avg Basket"]= st_agg["Revenue"]/st_agg["Txn"]

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("Stores",        f"{st_agg['Store ID'].nunique()}")
    k2.metric("Open",          f"{(st_agg['Store Status']=='Open').sum()}")
    k3.metric("Avg €/SQM",     f"€{st_agg['Sales/SQM'].mean():.0f}")
    k4.metric("Avg Basket",    f"€{st_agg['Avg Basket'].mean():.0f}")
    if not st_agg.empty:
        best = st_agg.loc[st_agg["Revenue"].idxmax()]
        k5.metric("Top Store", best["Store Name"], fmt(best["Revenue"]))

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
            xaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="€"),
            **CHART)
        st.plotly_chart(fig_sb, use_container_width=True)

    with cs2:
        fig_sc = px.scatter(
            st_agg, x="Sales/SQM", y="vs Bgt%",
            size="Revenue", color="Store Country",
            hover_name="Store Name",
            title="Efficiency · €/SQM vs vs Budget %",
            size_max=42,
            color_discrete_sequence=[C["blue"],C["amber"],C["green"],C["purple"]],
        )
        fig_sc.add_hline(y=0, line_dash="dash", line_color=C["red"], opacity=.5)
        fig_sc.add_vline(x=st_agg["Sales/SQM"].median(),
                         line_dash="dot", line_color=C["grey"], opacity=.4)
        fig_sc.update_layout(
            height=500,
            xaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="€"),
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
                          yaxis=dict(showgrid=True, gridcolor=C["grid"], tickprefix="€"),
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
                                        tickprefix="€"), **CHART)
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
                  "Store Status","Revenue","Budget Sales","vs Bgt%","GM%",
                  "Sales/SQM","Avg Basket"]].copy()
    tbl.columns = ["Store","Country","Channel","Format","Status",
                   "Revenue","Budget","vs Bgt%","GM%","€/SQM","Avg Basket"]
    st.dataframe(
        tbl.style
        .format({"Revenue":"€{:,.0f}","Budget":"€{:,.0f}",
                 "vs Bgt%":"{:+.1f}%","GM%":"{:.1f}%",
                 "€/SQM":"€{:.0f}","Avg Basket":"€{:.0f}"})
        .background_gradient(subset=["Revenue"], cmap="Blues")
        .map(lambda v: f"color:{'green' if v>=0 else 'red'}"
             if isinstance(v,(int,float)) else "", subset=["vs Bgt%"]),
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

    # ── Compute signals ────────────────────────────────────────────────────────
    net_s  = sales["Net Sales"].sum()
    tot_b  = budget["Budget Sales"].sum()
    vs_b   = (net_s / tot_b - 1) * 100 if tot_b else 0
    ly     = ly_net_sales()
    vs_ly  = (net_s / ly - 1) * 100 if ly else 0
    gross  = sales.loc[sales["Order Type"]=="Sales","Sales"].sum()
    ret    = sales.loc[sales["Order Type"]=="Return","Sales"].sum()
    ret_rt = ret / gross * 100 if gross else 0
    gm     = (net_s - sales["Net Cost"].sum()) / net_s * 100 if net_s else 0
    avg_disc = sales["Discount"].mean() * 100

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
             f"Net revenue is <b>{fmt(vs_b,'%')}</b> vs budget ({fmt(net_s)} vs {fmt(tot_b)}). "
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
             f"Revenue grew <b>{fmt(vs_ly,'%')}</b> vs prior year ({fmt(ly)} → {fmt(net_s)}). "
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
