import streamlit as st
import pandas as pd
from data.projects import calculate_co_impact


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

        st.metric("New Cost-to-Complete", f"${new_ctc:,.0f}",
                  delta=ctc_delta_str, delta_color="inverse")
        st.metric("New Total Budget", f"${new_total_budget:,.0f}",
                  delta=f"+${budget_delta:,.0f}", delta_color="inverse")
        variance_sign = "+" if new_variance > 0 else ""
        st.metric("New Variance %", f"{variance_sign}{new_variance * 100:.1f}%",
                  delta=f"{variance_sign}{new_variance * 100:.1f}%", delta_color="inverse")

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
