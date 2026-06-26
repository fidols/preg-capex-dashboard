# PREG Interview Prep — Design Spec
**Date:** 2026-06-25  
**Interview:** Monday 2026-06-29, 2:00 PM, with Adam (formerly Greystar)  
**Role:** Financial Analyst, CapEx — Post Real Estate Group

---

## What We're Building

Two deliverables:

1. **`wiki.md`** — A markdown knowledge base committed to GitHub. Covers PREG company background, CapEx domain vocabulary, Procore/Yardi conceptual workflows, LIHTC basics, Adam's Greystar context, and interview strategy. No app, no API — just a file Fidel reads to prep.

2. **CapEx Portfolio Dashboard** — A single Streamlit app demoed live during the interview. Uses real PREG property names scraped from their website and the HUD/LIHTC public database, with simulated financials layered on top.

---

## File Structure

```
post-real-estate/
├── app.py                  # Streamlit entry point, tab routing
├── data/
│   └── projects.py         # Simulated dataset built from real PREG properties
├── components/
│   ├── kpi_strip.py        # Top-row KPI metric cards
│   ├── portfolio.py        # Tab 1 — portfolio table + variance chart
│   ├── project_detail.py   # Tab 2 — single project drill-down
│   ├── change_order.py     # Tab 3 — change order impact calculator
│   └── reporting.py        # Tab 4 — weekly/monthly reporting view
├── styles/
│   └── theme.py            # PREG brand colors + custom CSS
├── wiki.md                 # Interview prep knowledge base
└── requirements.txt
```

---

## Data Model

Each project is a row in a pandas DataFrame. Fields:

| Field | Source |
|-------|--------|
| `project_name` | Scraped — PREG website / HUD LIHTC DB |
| `location` (city, state) | Scraped |
| `asset_type` | Scraped (Multifamily, Affordable/LIHTC, Industrial, Mobile Home Park) |
| `units` | Scraped |
| `original_budget` | Simulated — scaled to asset type + unit count |
| `committed_costs` | Simulated |
| `actual_spend` | Simulated |
| `pct_complete` | Simulated (0–100%) |
| `change_orders_count` | Simulated |
| `change_orders_amount` | Simulated |
| `cost_to_complete` | Derived: `original_budget - actual_spend` |
| `variance_pct` | Derived: `(actual_spend - original_budget) / original_budget` |
| `monthly_spend` | Simulated time series (list of monthly values) |

Budget ranges realistic for multifamily CapEx renovation: **$2M–$15M per property**, scaled by unit count. Numbers should read as credible to someone with Greystar institutional experience.

---

## UI Layout

### Header
PREG logo + "CapEx Portfolio Dashboard" title in PREG brand colors (pulled from their website).

### KPI Strip (always visible above tabs)
Five metric cards:
```
[ Total Budget ]  [ Total Committed ]  [ Total Spent ]  [ Remaining ]  [ Portfolio Variance % ]
```
Color-coded: green if under budget, red if over.

### Tab 1 — Portfolio Overview
- Sortable table: all projects with budget, committed, spent, variance %, % complete
- Horizontal bar chart: budget vs actual spend by project
- Clicking a project name in the table sets a session state variable that pre-selects it in Tab 2's dropdown

### Tab 2 — Project Detail
- Dropdown to select project
- Budget breakdown by category: Materials, Labor, Subcontractors, Contingency (stacked bar)
- Cost-to-complete gauge chart
- Change order history table (date, description, amount, cumulative impact)

### Tab 3 — Change Order Calculator
- Inputs: select project, enter change order amount + description
- Live outputs: new cost-to-complete, new variance %, impact on portfolio total
- Updates as user types — no submit button needed

### Tab 4 — Reporting
- Toggle: Weekly / Monthly view
- Line chart: cumulative spend over time vs budget line
- Summary table (project, period spend, cumulative, remaining) — formatted like an actual CapEx report

---

## Data Sourcing Strategy

1. **Scrape PREG website** for property portfolio: names, cities, unit counts, asset types
2. **Query HUD LIHTC public database** for their affordable housing assets
3. Deduplicate and normalize into 10–15 representative projects
4. Layer simulated financials on top with realistic multifamily CapEx ranges

---

## Knowledge Base (`wiki.md`) Sections

1. Post Real Estate Group — company overview, portfolio, vertical integration
2. The role — responsibilities, tools, what success looks like
3. CapEx domain vocabulary — full glossary
4. Procore and Yardi — conceptual workflows (what each system does, how they connect)
5. LIHTC basics — how affordable housing finance works
6. Adam / Greystar context — what institutional CapEx looks like, what he'll care about
7. Interview strategy — what to lead with, what to frame honestly, questions to ask Adam

---

## Tech Stack

- **Python 3.11+**
- **Streamlit** — app framework
- **Pandas** — data manipulation
- **Plotly** — charts (bar, line, gauge)
- **Requests / BeautifulSoup** — scraping (used during build, not at runtime)
- No database, no external APIs at runtime

---

## Success Criteria

- App loads in under 3 seconds on Fidel's laptop
- No runtime errors during a full tab-by-tab walkthrough
- Change order calculator updates live without page reload
- Numbers look realistic to someone with institutional real estate experience
- `wiki.md` covers every topic Fidel might be asked about cold
