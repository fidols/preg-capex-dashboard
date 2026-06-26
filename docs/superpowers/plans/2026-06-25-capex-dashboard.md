# CapEx Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page Streamlit CapEx portfolio dashboard using real PREG property names and simulated financials, demoed live during Fidel's interview on June 29, 2026.

**Architecture:** One Streamlit app (`app.py`) with a PREG-branded header, a persistent KPI strip, and four tabs (Portfolio Overview, Project Detail, Change Order Calculator, Reporting). Data is generated once at startup in `data/projects.py` as a pandas DataFrame using real PREG property names and seeded-random financials. Each tab is a separate component module. Session state (`st.session_state.selected_project`) links Tab 1 row selection to Tab 2 dropdown.

**Tech Stack:** Python 3.11+, Streamlit ≥1.35, pandas, plotly, pytest

---

### Task 1: Setup — requirements, directories, theme

**Files:**
- Create: `requirements.txt`
- Create: `styles/theme.py`
- Create: `data/__init__.py`, `components/__init__.py`, `styles/__init__.py`, `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
streamlit>=1.35.0
pandas>=2.0.0
plotly>=5.18.0
pytest>=8.0.0
```

- [ ] **Step 2: Create empty `__init__.py` files**

```bash
cd /Users/mr.fidols/post-real-estate
mkdir -p data components styles tests
touch data/__init__.py components/__init__.py styles/__init__.py tests/__init__.py
```

- [ ] **Step 3: Create `styles/theme.py`**

```python
PREG_BLUE = "#114F7E"
PREG_NAVY = "#1C355E"
PREG_LIGHT_BLUE = "#0075B0"
WHITE = "#FFFFFF"
LIGHT_GRAY = "#F8F9FA"
RED = "#C0392B"
GREEN = "#27AE60"
AMBER = "#F39C12"

PLOTLY_COLORS = {
    "budget": PREG_BLUE,
    "actual": PREG_LIGHT_BLUE,
    "committed": PREG_NAVY,
    "over_budget": RED,
    "under_budget": GREEN,
}

def inject_css() -> str:
    return f"""
    <style>
        .preg-header {{
            background-color: {PREG_NAVY};
            padding: 1.2rem 2rem;
            border-bottom: 4px solid {PREG_BLUE};
            margin-bottom: 1rem;
        }}
        .preg-header h1 {{
            color: {WHITE};
            font-size: 1.6rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: 0.05em;
        }}
        .preg-header p {{
            color: #BDC3C7;
            font-size: 0.85rem;
            margin: 0.2rem 0 0 0;
        }}
        .kpi-card {{
            background-color: {WHITE};
            border: 1px solid #DEE2E6;
            border-radius: 6px;
            padding: 1rem;
            text-align: center;
        }}
        div[data-testid="stMetricValue"] {{
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            color: {PREG_NAVY} !important;
        }}
    </style>
    """
```

- [ ] **Step 4: Install dependencies**

```bash
cd /Users/mr.fidols/post-real-estate
pip install -r requirements.txt
```

Expected: all packages install without errors.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt data/__init__.py components/__init__.py styles/__init__.py tests/__init__.py styles/theme.py
git commit -m "feat: add project structure, dependencies, and PREG theme"
```

---

### Task 2: Data layer — projects.py

**Files:**
- Create: `data/projects.py`
- Create: `tests/test_projects.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_projects.py
import pytest
import pandas as pd
from data.projects import generate_projects, MONTHS, calculate_co_impact

REQUIRED_COLUMNS = [
    "project_name", "city", "state", "units", "asset_type",
    "original_budget", "committed_costs", "actual_spend",
    "pct_complete", "change_orders_count", "change_orders_amount",
    "cost_to_complete", "variance_pct", "monthly_spend",
]


def test_generate_projects_returns_dataframe():
    df = generate_projects()
    assert isinstance(df, pd.DataFrame)


def test_generate_projects_has_12_rows():
    df = generate_projects()
    assert len(df) == 12


def test_generate_projects_has_required_columns():
    df = generate_projects()
    for col in REQUIRED_COLUMNS:
        assert col in df.columns, f"Missing column: {col}"


def test_generate_projects_is_deterministic():
    df1 = generate_projects()
    df2 = generate_projects()
    pd.testing.assert_frame_equal(df1, df2)


def test_budgets_are_positive():
    df = generate_projects()
    assert (df["original_budget"] > 0).all()


def test_actual_spend_does_not_exceed_budget_by_more_than_20_pct():
    df = generate_projects()
    ratio = df["actual_spend"] / df["original_budget"]
    assert (ratio < 1.20).all()


def test_pct_complete_is_between_0_and_1():
    df = generate_projects()
    assert (df["pct_complete"] >= 0).all()
    assert (df["pct_complete"] <= 1).all()


def test_monthly_spend_has_6_values_per_project():
    df = generate_projects()
    for _, row in df.iterrows():
        assert len(row["monthly_spend"]) == 6


def test_months_has_6_entries():
    assert len(MONTHS) == 6


def test_calculate_co_impact_increases_cost_to_complete():
    df = generate_projects()
    project = df["project_name"].iloc[0]
    original_ctc = df.loc[df["project_name"] == project, "cost_to_complete"].iloc[0]
    new_ctc, new_variance = calculate_co_impact(df, project, 100_000)
    assert new_ctc == original_ctc + 100_000


def test_calculate_co_impact_with_zero_amount_is_unchanged():
    df = generate_projects()
    project = df["project_name"].iloc[0]
    original_ctc = df.loc[df["project_name"] == project, "cost_to_complete"].iloc[0]
    new_ctc, _ = calculate_co_impact(df, project, 0)
    assert new_ctc == original_ctc
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/mr.fidols/post-real-estate
pytest tests/test_projects.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'data.projects'`

- [ ] **Step 3: Create `data/projects.py`**

```python
import random
import pandas as pd

MONTHS = ["Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026", "May 2026", "Jun 2026"]

_PROPERTIES = [
    {"name": "San Regis", "city": "Van Nuys", "state": "CA", "units": 390, "asset_type": "Affordable Conversion"},
    {"name": "Chaparral Apartments", "city": "Palmdale", "state": "CA", "units": 296, "asset_type": "Multifamily"},
    {"name": "The Marquee", "city": "Los Angeles", "state": "CA", "units": 236, "asset_type": "Multifamily"},
    {"name": "Avenues at Kennesaw", "city": "Kennesaw", "state": "GA", "units": 524, "asset_type": "Multifamily"},
    {"name": "Rosemont Peachtree Corners", "city": "Norcross", "state": "GA", "units": 440, "asset_type": "Multifamily"},
    {"name": "Valera Riverside", "city": "Lithia Springs", "state": "GA", "units": 425, "asset_type": "LIHTC"},
    {"name": "Tribute Verdae", "city": "Greenville", "state": "SC", "units": 268, "asset_type": "Affordable Conversion"},
    {"name": "The Paddock Club Columbia", "city": "Columbia", "state": "SC", "units": 336, "asset_type": "Bond Financed"},
    {"name": "Magnolia", "city": "Charleston", "state": "SC", "units": 312, "asset_type": "Multifamily"},
    {"name": "Viewcrest Village", "city": "Bremerton", "state": "WA", "units": 300, "asset_type": "LIHTC"},
    {"name": "Village at Broadstone Station", "city": "Apex", "state": "NC", "units": 300, "asset_type": "Multifamily"},
    {"name": "Inwood Crossing", "city": "Wichita", "state": "KS", "units": 260, "asset_type": "Multifamily"},
]


def generate_projects() -> pd.DataFrame:
    rng = random.Random(42)
    rows = []

    for p in _PROPERTIES:
        budget_per_unit = rng.uniform(6_000, 14_000)
        original_budget = round(p["units"] * budget_per_unit / 1_000) * 1_000

        pct_complete = round(rng.uniform(0.12, 0.88), 2)

        variance_factor = rng.uniform(0.93, 1.11)
        actual_spend = round(original_budget * pct_complete * variance_factor / 100) * 100

        num_cos = rng.randint(0, 3)
        co_amount = round(sum(rng.uniform(50_000, 220_000) for _ in range(num_cos)) / 100) * 100

        committed_costs = round(
            (actual_spend + (original_budget - actual_spend) * rng.uniform(0.55, 0.85)) / 100
        ) * 100
        committed_costs = min(committed_costs, original_budget + co_amount)

        cost_to_complete = max(original_budget + co_amount - actual_spend, 0)

        expected_spend = original_budget * pct_complete
        variance_pct = round((actual_spend - expected_spend) / expected_spend, 4) if expected_spend > 0 else 0.0

        monthly_spend = _generate_monthly_spend(actual_spend, rng)

        rows.append({
            "project_name": p["name"],
            "city": p["city"],
            "state": p["state"],
            "units": p["units"],
            "asset_type": p["asset_type"],
            "original_budget": original_budget,
            "committed_costs": committed_costs,
            "actual_spend": actual_spend,
            "pct_complete": pct_complete,
            "change_orders_count": num_cos,
            "change_orders_amount": co_amount,
            "cost_to_complete": cost_to_complete,
            "variance_pct": variance_pct,
            "monthly_spend": monthly_spend,
        })

    return pd.DataFrame(rows)


def _generate_monthly_spend(total: float, rng: random.Random) -> list[float]:
    weights = sorted([rng.uniform(0.08, 0.25) for _ in range(6)])
    total_weight = sum(weights)
    return [round(total * w / total_weight / 100) * 100 for w in weights]


def calculate_co_impact(df: pd.DataFrame, project_name: str, co_amount: float) -> tuple[float, float]:
    row = df[df["project_name"] == project_name].iloc[0]
    new_ctc = row["cost_to_complete"] + co_amount
    new_budget = row["original_budget"] + row["change_orders_amount"] + co_amount
    expected_spend = new_budget * row["pct_complete"]
    new_variance = (row["actual_spend"] - expected_spend) / expected_spend if expected_spend > 0 else 0.0
    return new_ctc, round(new_variance, 4)
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/mr.fidols/post-real-estate
pytest tests/test_projects.py -v
```

Expected: all 12 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add data/projects.py tests/test_projects.py
git commit -m "feat: add data layer with 12 real PREG properties and seeded financials"
```

---

### Task 3: KPI strip component

**Files:**
- Create: `components/kpi_strip.py`

- [ ] **Step 1: Create `components/kpi_strip.py`**

```python
import streamlit as st
import pandas as pd
from styles.theme import GREEN, RED


def render_kpi_strip(df: pd.DataFrame) -> None:
    total_budget = df["original_budget"].sum() + df["change_orders_amount"].sum()
    total_committed = df["committed_costs"].sum()
    total_spent = df["actual_spend"].sum()
    total_remaining = total_budget - total_spent
    expected_spend = (df["original_budget"] * df["pct_complete"]).sum()
    portfolio_variance_pct = (total_spent - expected_spend) / expected_spend if expected_spend > 0 else 0.0

    cols = st.columns(5)

    with cols[0]:
        st.metric("Total Budget", f"${total_budget / 1_000_000:.1f}M")

    with cols[1]:
        st.metric("Total Committed", f"${total_committed / 1_000_000:.1f}M")

    with cols[2]:
        st.metric("Total Spent", f"${total_spent / 1_000_000:.1f}M")

    with cols[3]:
        remaining_delta = f"-${abs(total_remaining) / 1_000_000:.1f}M" if total_remaining < 0 else f"${total_remaining / 1_000_000:.1f}M remaining"
        st.metric("Remaining", f"${total_remaining / 1_000_000:.1f}M")

    with cols[4]:
        variance_color = RED if portfolio_variance_pct > 0 else GREEN
        sign = "+" if portfolio_variance_pct > 0 else ""
        st.metric(
            "Portfolio Variance",
            f"{sign}{portfolio_variance_pct * 100:.1f}%",
            delta=f"{sign}{portfolio_variance_pct * 100:.1f}%",
            delta_color="inverse",
        )
```

- [ ] **Step 2: Smoke test — verify it imports without error**

```bash
cd /Users/mr.fidols/post-real-estate
python -c "from components.kpi_strip import render_kpi_strip; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add components/kpi_strip.py
git commit -m "feat: add KPI strip component with 5 portfolio metrics"
```

---

### Task 4: Portfolio Overview tab (Tab 1)

**Files:**
- Create: `components/portfolio.py`

- [ ] **Step 1: Create `components/portfolio.py`**

```python
import streamlit as st
import pandas as pd
import plotly.express as px
from styles.theme import PREG_BLUE, PREG_LIGHT_BLUE, RED, GREEN


def render_portfolio_tab(df: pd.DataFrame) -> None:
    st.subheader("Portfolio Overview")

    display_df = df[[
        "project_name", "city", "state", "units", "asset_type",
        "original_budget", "actual_spend", "committed_costs",
        "pct_complete", "change_orders_count", "variance_pct",
    ]].copy()

    display_df.columns = [
        "Project", "City", "State", "Units", "Asset Type",
        "Budget ($)", "Spent ($)", "Committed ($)",
        "% Complete", "# COs", "Variance %",
    ]

    display_df["Budget ($)"] = display_df["Budget ($)"].map("${:,.0f}".format)
    display_df["Spent ($)"] = display_df["Spent ($)"].map("${:,.0f}".format)
    display_df["Committed ($)"] = display_df["Committed ($)"].map("${:,.0f}".format)
    display_df["% Complete"] = (display_df["% Complete"] * 100).map("{:.0f}%".format)
    display_df["Variance %"] = display_df["Variance %"].map(
        lambda v: f"+{v*100:.1f}%" if v > 0 else f"{v*100:.1f}%"
    )

    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="portfolio_table",
    )

    if event.selection.rows:
        selected_idx = event.selection.rows[0]
        st.session_state.selected_project = df["project_name"].iloc[selected_idx]
        st.info(f"Selected: **{st.session_state.selected_project}** — switch to Project Detail tab to drill in.")

    st.divider()
    st.subheader("Budget vs. Actual Spend by Project")

    chart_df = df[["project_name", "original_budget", "actual_spend"]].copy()
    chart_df = chart_df.sort_values("original_budget", ascending=True)

    fig = px.bar(
        chart_df,
        y="project_name",
        x=["original_budget", "actual_spend"],
        orientation="h",
        barmode="group",
        labels={
            "project_name": "",
            "value": "Amount ($)",
            "variable": "",
        },
        color_discrete_map={
            "original_budget": PREG_BLUE,
            "actual_spend": PREG_LIGHT_BLUE,
        },
        height=500,
    )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#333333"),
    )

    newnames = {"original_budget": "Budget", "actual_spend": "Actual Spend"}
    fig.for_each_trace(lambda t: t.update(name=newnames.get(t.name, t.name)))

    st.plotly_chart(fig, use_container_width=True)
```

- [ ] **Step 2: Smoke test**

```bash
cd /Users/mr.fidols/post-real-estate
python -c "from components.portfolio import render_portfolio_tab; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add components/portfolio.py
git commit -m "feat: add Portfolio Overview tab with sortable table and bar chart"
```

---

### Task 5: Project Detail tab (Tab 2)

**Files:**
- Create: `components/project_detail.py`

- [ ] **Step 1: Create `components/project_detail.py`**

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from styles.theme import PREG_BLUE, PREG_NAVY, PREG_LIGHT_BLUE, RED, GREEN, AMBER


_BUDGET_CATEGORIES = {
    "Labor": 0.35,
    "Materials": 0.30,
    "Subcontractors": 0.25,
    "Contingency": 0.10,
}


def render_project_detail_tab(df: pd.DataFrame) -> None:
    st.subheader("Project Detail")

    default_project = st.session_state.get("selected_project", df["project_name"].iloc[0])
    if default_project not in df["project_name"].values:
        default_project = df["project_name"].iloc[0]
    default_idx = df["project_name"].tolist().index(default_project)

    selected = st.selectbox(
        "Select Project",
        options=df["project_name"].tolist(),
        index=default_idx,
        key="detail_project_select",
    )
    st.session_state.selected_project = selected

    row = df[df["project_name"] == selected].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Original Budget", f"${row['original_budget']:,.0f}")
    col2.metric("Actual Spend", f"${row['actual_spend']:,.0f}")
    col3.metric("% Complete", f"{row['pct_complete']*100:.0f}%")
    variance_sign = "+" if row["variance_pct"] > 0 else ""
    col4.metric(
        "Variance",
        f"{variance_sign}{row['variance_pct']*100:.1f}%",
        delta=f"{variance_sign}{row['variance_pct']*100:.1f}%",
        delta_color="inverse",
    )

    st.divider()
    left, right = st.columns(2)

    with left:
        st.markdown("**Budget by Category**")
        total = row["original_budget"]
        cat_df = pd.DataFrame([
            {"Category": cat, "Amount": total * pct}
            for cat, pct in _BUDGET_CATEGORIES.items()
        ])
        fig_bar = px.bar(
            cat_df,
            x="Category",
            y="Amount",
            color="Category",
            color_discrete_sequence=[PREG_NAVY, PREG_BLUE, PREG_LIGHT_BLUE, AMBER],
            labels={"Amount": "Budget ($)"},
            height=300,
        )
        fig_bar.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)

    with right:
        st.markdown("**Cost-to-Complete**")
        total_budget_incl_co = row["original_budget"] + row["change_orders_amount"]
        ctc = row["cost_to_complete"]
        ctc_pct = ctc / total_budget_incl_co if total_budget_incl_co > 0 else 0

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=ctc,
            number={"prefix": "$", "valueformat": ",.0f"},
            delta={"reference": total_budget_incl_co, "valueformat": ",.0f", "prefix": "Budget: $"},
            gauge={
                "axis": {"range": [0, total_budget_incl_co]},
                "bar": {"color": PREG_BLUE},
                "steps": [
                    {"range": [0, total_budget_incl_co * 0.25], "color": "#EBF5FB"},
                    {"range": [total_budget_incl_co * 0.25, total_budget_incl_co * 0.75], "color": "#D6EAF8"},
                    {"range": [total_budget_incl_co * 0.75, total_budget_incl_co], "color": "#AED6F1"},
                ],
                "threshold": {
                    "line": {"color": RED, "width": 3},
                    "thickness": 0.75,
                    "value": total_budget_incl_co,
                },
            },
            title={"text": f"Remaining to spend<br><span style='font-size:0.8em'>{ctc_pct*100:.0f}% of budget remaining</span>"},
        ))
        fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=0))
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.divider()
    st.markdown("**Change Order History**")

    if row["change_orders_count"] == 0:
        st.info("No change orders on this project.")
    else:
        import random
        rng = random.Random(hash(selected))
        co_rows = []
        cumulative = 0
        for i in range(int(row["change_orders_count"])):
            amount = round(row["change_orders_amount"] / row["change_orders_count"] * rng.uniform(0.7, 1.3) / 100) * 100
            cumulative += amount
            co_rows.append({
                "CO #": f"CO-{i+1:03d}",
                "Description": rng.choice([
                    "Unforeseen structural repairs",
                    "MEP system upgrade",
                    "Site condition change",
                    "Owner-directed scope addition",
                    "Material price escalation",
                    "Subcontractor default replacement",
                ]),
                "Amount": f"${amount:,.0f}",
                "Status": "Approved",
                "Cumulative Impact": f"${cumulative:,.0f}",
            })
        st.dataframe(pd.DataFrame(co_rows), use_container_width=True, hide_index=True)
```

- [ ] **Step 2: Smoke test**

```bash
cd /Users/mr.fidols/post-real-estate
python -c "from components.project_detail import render_project_detail_tab; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add components/project_detail.py
git commit -m "feat: add Project Detail tab with budget breakdown, CTC gauge, CO history"
```

---

### Task 6: Change Order Calculator tab (Tab 3)

**Files:**
- Create: `components/change_order.py`

- [ ] **Step 1: Create `components/change_order.py`**

```python
import streamlit as st
import pandas as pd
from data.projects import calculate_co_impact
from styles.theme import RED, GREEN, AMBER


def render_change_order_tab(df: pd.DataFrame) -> None:
    st.subheader("Change Order Impact Calculator")
    st.markdown("Model the financial impact of a new change order before approving it.")

    col_input, col_results = st.columns([1, 1])

    with col_input:
        st.markdown("**New Change Order Details**")
        selected = st.selectbox(
            "Project",
            options=df["project_name"].tolist(),
            key="co_calc_project",
        )
        co_amount = st.number_input(
            "Change Order Amount ($)",
            min_value=0,
            max_value=5_000_000,
            value=100_000,
            step=5_000,
            key="co_calc_amount",
        )
        st.text_input("Description (optional)", placeholder="e.g. Unforeseen MEP repairs", key="co_calc_desc")

    row = df[df["project_name"] == selected].iloc[0]
    new_ctc, new_variance = calculate_co_impact(df, selected, co_amount)
    new_total_budget = row["original_budget"] + row["change_orders_amount"] + co_amount

    with col_results:
        st.markdown("**Projected Impact**")

        original_ctc = row["cost_to_complete"]
        ctc_delta = new_ctc - original_ctc
        ctc_delta_str = f"+${ctc_delta:,.0f}" if ctc_delta >= 0 else f"-${abs(ctc_delta):,.0f}"

        original_budget_total = row["original_budget"] + row["change_orders_amount"]
        budget_delta = new_total_budget - original_budget_total

        st.metric(
            "New Cost-to-Complete",
            f"${new_ctc:,.0f}",
            delta=ctc_delta_str,
            delta_color="inverse",
        )
        st.metric(
            "New Total Budget",
            f"${new_total_budget:,.0f}",
            delta=f"+${budget_delta:,.0f}",
            delta_color="inverse",
        )
        variance_sign = "+" if new_variance > 0 else ""
        st.metric(
            "New Variance %",
            f"{variance_sign}{new_variance * 100:.1f}%",
            delta=f"{variance_sign}{new_variance * 100:.1f}%",
            delta_color="inverse",
        )

    st.divider()
    st.markdown("**Portfolio-Level Impact**")

    portfolio_budget = df["original_budget"].sum() + df["change_orders_amount"].sum()
    portfolio_spent = df["actual_spend"].sum()
    new_portfolio_budget = portfolio_budget + co_amount
    new_portfolio_remaining = new_portfolio_budget - portfolio_spent

    p_col1, p_col2, p_col3 = st.columns(3)
    p_col1.metric("Portfolio Budget (before)", f"${portfolio_budget / 1_000_000:.2f}M")
    p_col2.metric("Portfolio Budget (after)", f"${new_portfolio_budget / 1_000_000:.2f}M",
                  delta=f"+${co_amount / 1_000:.0f}K", delta_color="inverse")
    p_col3.metric("Portfolio Remaining (after)", f"${new_portfolio_remaining / 1_000_000:.2f}M")

    if co_amount > 0:
        pct_of_budget = co_amount / portfolio_budget * 100
        if pct_of_budget < 0.5:
            color, msg = "green", "Low portfolio impact"
        elif pct_of_budget < 2.0:
            color, msg = "orange", "Moderate portfolio impact — flag for leadership"
        else:
            color, msg = "red", "High portfolio impact — escalate before approval"
        st.markdown(f":{color}[**{msg}** — this CO is {pct_of_budget:.2f}% of total portfolio budget]")
```

- [ ] **Step 2: Smoke test**

```bash
cd /Users/mr.fidols/post-real-estate
python -c "from components.change_order import render_change_order_tab; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add components/change_order.py
git commit -m "feat: add Change Order Calculator tab with live portfolio impact"
```

---

### Task 7: Reporting tab (Tab 4)

**Files:**
- Create: `components/reporting.py`

- [ ] **Step 1: Create `components/reporting.py`**

```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.projects import MONTHS
from styles.theme import PREG_BLUE, PREG_NAVY, PREG_LIGHT_BLUE, AMBER


def render_reporting_tab(df: pd.DataFrame) -> None:
    st.subheader("CapEx Reporting")

    view = st.radio(
        "View",
        options=["Monthly", "Weekly"],
        horizontal=True,
        key="reporting_view",
    )

    if view == "Monthly":
        _render_monthly(df)
    else:
        _render_weekly(df)


def _render_monthly(df: pd.DataFrame) -> None:
    portfolio_monthly = [
        sum(row["monthly_spend"][i] for _, row in df.iterrows())
        for i in range(6)
    ]
    portfolio_cumulative = []
    running = 0
    for m in portfolio_monthly:
        running += m
        portfolio_cumulative.append(running)

    total_budget = df["original_budget"].sum() + df["change_orders_amount"].sum()
    budget_line = [total_budget * (i + 1) / 6 for i in range(6)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=MONTHS, y=portfolio_cumulative,
        mode="lines+markers",
        name="Cumulative Spend",
        line=dict(color=PREG_BLUE, width=3),
        marker=dict(size=8),
    ))
    fig.add_trace(go.Scatter(
        x=MONTHS, y=budget_line,
        mode="lines",
        name="Budget Pace",
        line=dict(color=AMBER, width=2, dash="dash"),
    ))
    fig.update_layout(
        title="Portfolio Cumulative Spend vs. Budget Pace",
        yaxis_title="Cumulative Spend ($)",
        xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("**Monthly CapEx Summary**")

    summary_rows = []
    for _, row in df.iterrows():
        monthly = row["monthly_spend"]
        summary_rows.append({
            "Project": row["project_name"],
            "State": row["state"],
            **{MONTHS[i]: f"${monthly[i]:,.0f}" for i in range(6)},
            "YTD Total": f"${sum(monthly):,.0f}",
            "Budget": f"${row['original_budget']:,.0f}",
            "Remaining": f"${row['cost_to_complete']:,.0f}",
        })

    totals = {"Project": "TOTAL", "State": ""}
    for i, month in enumerate(MONTHS):
        totals[month] = f"${sum(row['monthly_spend'][i] for _, row in df.iterrows()):,.0f}"
    totals["YTD Total"] = f"${df['actual_spend'].sum():,.0f}"
    totals["Budget"] = f"${(df['original_budget'].sum() + df['change_orders_amount'].sum()):,.0f}"
    totals["Remaining"] = f"${df['cost_to_complete'].sum():,.0f}"
    summary_rows.append(totals)

    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)


def _render_weekly(df: pd.DataFrame) -> None:
    weeks = [f"W{i+1} ({MONTHS[-1].split()[0]})" for i in range(4)] + \
            [f"W{i+1} ({MONTHS[-1]})" for i in range(4)]
    weeks = [f"Wk {i+1}" for i in range(8)]

    portfolio_weekly = []
    for _, row in df.iterrows():
        last_month = row["monthly_spend"][-1]
        weekly = [round(last_month * w / sum([1, 1.2, 0.9, 1.1, 1.0, 0.8, 1.3, 0.9]) / 100) * 100
                  for w in [1, 1.2, 0.9, 1.1, 1.0, 0.8, 1.3, 0.9]]
        portfolio_weekly.append(weekly)

    totals = [sum(portfolio_weekly[j][i] for j in range(len(df))) for i in range(8)]
    cumulative = []
    running = df["actual_spend"].sum() - sum(totals)
    for t in totals:
        running += t
        cumulative.append(running)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weeks, y=totals,
        name="Weekly Spend",
        marker_color=PREG_LIGHT_BLUE,
    ))
    fig.add_trace(go.Scatter(
        x=weeks, y=cumulative,
        mode="lines+markers",
        name="Cumulative",
        line=dict(color=PREG_BLUE, width=2),
        yaxis="y2",
    ))
    fig.update_layout(
        title="Weekly CapEx Activity (Last 8 Weeks)",
        yaxis=dict(title="Weekly Spend ($)"),
        yaxis2=dict(title="Cumulative Spend ($)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("**Weekly Summary (Last 8 Weeks)**")

    summary_rows = []
    for j, (_, row) in enumerate(df.iterrows()):
        summary_rows.append({
            "Project": row["project_name"],
            **{weeks[i]: f"${portfolio_weekly[j][i]:,.0f}" for i in range(8)},
            "8-Wk Total": f"${sum(portfolio_weekly[j]):,.0f}",
        })

    total_row = {"Project": "TOTAL"}
    for i in range(8):
        total_row[weeks[i]] = f"${totals[i]:,.0f}"
    total_row["8-Wk Total"] = f"${sum(totals):,.0f}"
    summary_rows.append(total_row)

    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
```

- [ ] **Step 2: Smoke test**

```bash
cd /Users/mr.fidols/post-real-estate
python -c "from components.reporting import render_reporting_tab; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add components/reporting.py
git commit -m "feat: add Reporting tab with monthly/weekly toggle and summary table"
```

---

### Task 8: Main app — wire everything together

**Files:**
- Create: `app.py`

- [ ] **Step 1: Create `app.py`**

```python
import streamlit as st
from data.projects import generate_projects
from components.kpi_strip import render_kpi_strip
from components.portfolio import render_portfolio_tab
from components.project_detail import render_project_detail_tab
from components.change_order import render_change_order_tab
from components.reporting import render_reporting_tab
from styles.theme import inject_css, PREG_NAVY

st.set_page_config(
    page_title="Post Real Estate Group — CapEx Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(inject_css(), unsafe_allow_html=True)

st.markdown(
    """
    <div class="preg-header">
        <h1>POST REAL ESTATE GROUP</h1>
        <p>CapEx Portfolio Dashboard &nbsp;·&nbsp; FY 2026 &nbsp;·&nbsp; 12 Active Projects</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "selected_project" not in st.session_state:
    st.session_state.selected_project = None

df = generate_projects()

render_kpi_strip(df)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Portfolio Overview",
    "🔍 Project Detail",
    "🔧 Change Order Calculator",
    "📈 Reporting",
])

with tab1:
    render_portfolio_tab(df)

with tab2:
    render_project_detail_tab(df)

with tab3:
    render_change_order_tab(df)

with tab4:
    render_reporting_tab(df)
```

- [ ] **Step 2: Run the app**

```bash
cd /Users/mr.fidols/post-real-estate
streamlit run app.py
```

Expected: browser opens at `http://localhost:8501` showing PREG header, 5 KPI cards, 4 tabs.

- [ ] **Step 3: Manual smoke test — walk through all tabs**

Check each of the following in the browser:

- [ ] KPI strip shows 5 metrics with dollar amounts (not zeros, not errors)
- [ ] Tab 1: table shows 12 projects; bar chart renders with 2 bars per project
- [ ] Tab 1: click a row → blue info message appears with selected project name
- [ ] Tab 2: dropdown defaults to first project; all 4 metrics show; gauge chart renders; CO history shows (or "No change orders" for projects with 0)
- [ ] Tab 2: switch dropdown to a project that had a row click in Tab 1 → it pre-selects correctly
- [ ] Tab 3: change number input → all 3 impact metrics update; portfolio metrics update; color-coded flag appears
- [ ] Tab 4: Monthly view → line chart + summary table with totals row
- [ ] Tab 4: toggle to Weekly → bar+line chart + weekly summary table

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: wire all tabs into main Streamlit app - dashboard complete"
```

---

### Task 9: Run full test suite and final commit

**Files:**
- No new files

- [ ] **Step 1: Run all tests**

```bash
cd /Users/mr.fidols/post-real-estate
pytest tests/ -v
```

Expected: 12 tests PASS, 0 failures.

- [ ] **Step 2: Verify app loads cleanly with no console errors**

```bash
streamlit run app.py
```

Open browser → check terminal for any red error output. Expected: none.

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: CapEx dashboard complete - 12 PREG properties, 4 tabs, PREG branding"
```
