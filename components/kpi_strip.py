import streamlit as st
import pandas as pd


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
        st.metric("Remaining", f"${total_remaining / 1_000_000:.1f}M")

    with cols[4]:
        sign = "+" if portfolio_variance_pct > 0 else ""
        st.metric(
            "Portfolio Variance",
            f"{sign}{portfolio_variance_pct * 100:.1f}%",
            delta=f"{sign}{portfolio_variance_pct * 100:.1f}%",
            delta_color="inverse",
        )
