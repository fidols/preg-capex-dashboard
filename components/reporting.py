import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.projects import MONTHS
from styles.theme import PREG_BLUE, PREG_LIGHT_BLUE, AMBER


def render_reporting_tab(df: pd.DataFrame) -> None:
    st.subheader("CapEx Reporting")

    view = st.radio("View", options=["Monthly", "Weekly"], horizontal=True, key="reporting_view")

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
    running = 0.0
    for m in portfolio_monthly:
        running += m
        portfolio_cumulative.append(running)

    total_budget = df["original_budget"].sum() + df["change_orders_amount"].sum()
    budget_line = [total_budget * (i + 1) / 6 for i in range(6)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=MONTHS, y=portfolio_cumulative,
        mode="lines+markers", name="Cumulative Spend",
        line=dict(color=PREG_BLUE, width=3), marker=dict(size=8),
    ))
    fig.add_trace(go.Scatter(
        x=MONTHS, y=budget_line,
        mode="lines", name="Budget Pace",
        line=dict(color=AMBER, width=2, dash="dash"),
    ))
    fig.update_layout(
        title="Portfolio Cumulative Spend vs. Budget Pace",
        yaxis_title="Cumulative Spend ($)", xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white", height=350, margin=dict(l=0, r=0, t=40, b=0),
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
    weeks = [f"Wk {i+1}" for i in range(8)]
    _weights = [1, 1.2, 0.9, 1.1, 1.0, 0.8, 1.3, 0.9]
    _weight_sum = sum(_weights)

    portfolio_weekly = []
    for _, row in df.iterrows():
        last_month = row["monthly_spend"][-1]
        weekly = [round(last_month * w / _weight_sum / 100) * 100 for w in _weights]
        portfolio_weekly.append(weekly)

    totals = [sum(portfolio_weekly[j][i] for j in range(len(df))) for i in range(8)]
    cumulative = []
    running = df["actual_spend"].sum() - sum(totals)
    for t in totals:
        running += t
        cumulative.append(running)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=weeks, y=totals, name="Weekly Spend", marker_color=PREG_LIGHT_BLUE))
    fig.add_trace(go.Scatter(
        x=weeks, y=cumulative, mode="lines+markers", name="Cumulative",
        line=dict(color=PREG_BLUE, width=2), yaxis="y2",
    ))
    fig.update_layout(
        title="Weekly CapEx Activity (Last 8 Weeks)",
        yaxis=dict(title="Weekly Spend ($)"),
        yaxis2=dict(title="Cumulative Spend ($)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white", height=350, margin=dict(l=0, r=0, t=40, b=0),
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
