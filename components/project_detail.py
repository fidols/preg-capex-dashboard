import random
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from styles.theme import PREG_BLUE, PREG_NAVY, PREG_LIGHT_BLUE, AMBER, RED, section_banner


_BUDGET_CATEGORIES = {
    "Labor": 0.35,
    "Materials": 0.30,
    "Subcontractors": 0.25,
    "Contingency": 0.10,
}


def render_project_detail_tab(df: pd.DataFrame) -> None:
    section_banner("CapEx Dashboard", "Project Detail")

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
