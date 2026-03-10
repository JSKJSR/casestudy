# Intersport · C-Suite Sales Dashboard

A Power BI-style multi-page dashboard built with **Streamlit + Plotly**.

## Deploy to Streamlit Cloud

### Step 1 — Push to GitHub
```bash
cd IntersportCaseStudy
git init
git add dashboard.py requirements.txt README.md .gitignore
git commit -m "Initial dashboard"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository, branch `main`, and set **Main file path** to `dashboard.py`
5. Click **"Deploy"**

### Step 3 — Use the app
Once deployed, open the app URL and **upload the Excel file** via the sidebar.
The data is cached for your session — no file is stored on the server.

---

## Run Locally
```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## Pages
| Page | What it shows |
|---|---|
| **Executive Summary** | KPIs, monthly trend vs Budget/LY, quarterly heatmap, geography |
| **Sales Performance** | Budget variance, YoY growth, rolling averages, returns, discounts |
| **Product & Category** | Treemap, bestsellers, slow movers with images, margin by category |
| **Store Network** | Per-store KPIs, LFL analysis, area manager view, detail table |

## Sidebar Filters
Year · Country · Channel · Product Category — all charts update live.
