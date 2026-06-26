import streamlit as st
import pandas as pd
import plotly.express as px
from styles.theme import PREG_BLUE, PREG_LIGHT_BLUE, section_banner


def render_portfolio_tab(df: pd.DataFrame) -> None:
    section_banner("CapEx Dashboard", "Portfolio Overview")

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
    section_banner("Portfolio Analysis", "Budget vs. Actual Spend by Project")

    chart_df = df[["project_name", "original_budget", "actual_spend"]].copy()
    chart_df = chart_df.sort_values("original_budget", ascending=True)

    fig = px.bar(
        chart_df,
        y="project_name",
        x=["original_budget", "actual_spend"],
        orientation="h",
        barmode="group",
        labels={"project_name": "", "value": "Amount ($)", "variable": ""},
        color_discrete_map={"original_budget": PREG_BLUE, "actual_spend": PREG_LIGHT_BLUE},
        height=500,
    )
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#333333"),
    )
    newnames = {"original_budget": "Budget", "actual_spend": "Actual Spend"}
    fig.for_each_trace(lambda t: t.update(name=newnames.get(t.name, t.name)))

    st.plotly_chart(fig, use_container_width=True)
