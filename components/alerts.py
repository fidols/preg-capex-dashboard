import streamlit as st
import pandas as pd
from styles.theme import section_banner, PREG_NAVY, WHITE

_RED_THRESHOLD = 0.05    # |variance| >= 5% = red
_YELLOW_THRESHOLD = 0.025 # |variance| >= 2.5% = yellow, else green
_CO_HIGH_THRESHOLD = 3    # 3+ change orders = flag


def _classify(row: pd.Series) -> tuple:
    v = row["variance_pct"]
    cos = row["change_orders_count"]
    abs_v = abs(v)

    if abs_v >= _RED_THRESHOLD:
        color = "#C0392B"
        label = "RED"
        if v > 0:
            status = "Over Budget"
            if cos >= _CO_HIGH_THRESHOLD:
                action = (
                    f"Variance +{v*100:.1f}% with {cos} COs — audit CO log for unapproved items, "
                    "hold next pay app pending PM sign-off, escalate to Adam."
                )
            else:
                action = (
                    f"Variance +{v*100:.1f}% — review subcontractor billings against Schedule of Values, "
                    "confirm no unapproved scope additions, flag before next pay app."
                )
        else:
            status = "Significantly Under-Paced"
            action = (
                f"Variance {v*100:.1f}% — contact GC immediately for updated schedule. "
                "Determine if this is a billing lag or construction stoppage. "
                "Notify asset management — cash flow projections and investor reporting may need revision."
            )
    elif abs_v >= _YELLOW_THRESHOLD:
        color = "#E67E22"
        label = "YELLOW"
        if v > 0:
            status = "Slightly Over Budget"
            action = (
                f"Variance +{v*100:.1f}% — monitor closely. Confirm current billings match "
                "approved scope before next pay app."
            )
        else:
            status = "Slightly Under-Paced"
            action = (
                f"Variance {v*100:.1f}% — verify with GC that billing is current. "
                "Watch for acceleration in upcoming pay apps."
            )
    else:
        status = "On Track"
        color = "#27AE60"
        label = "GREEN"
        action = "No action required. Monitor at next monthly review."

    return status, color, label, action


def render_alerts_tab(df: pd.DataFrame) -> None:
    section_banner("Portfolio Intelligence", "Portfolio Alerts")

    st.markdown(
        "Real-time variance flags with recommended actions. "
        "Red = immediate attention. Yellow = monitor closely. Green = on track."
    )

    col1, col2, col3 = st.columns(3)
    red_count = int((df["variance_pct"].abs() >= _RED_THRESHOLD).sum())
    yellow_count = int(
        ((df["variance_pct"].abs() >= _YELLOW_THRESHOLD) &
         (df["variance_pct"].abs() < _RED_THRESHOLD)).sum()
    )
    green_count = int(len(df) - red_count - yellow_count)

    col1.metric("Immediate Action", f"{red_count} projects", delta=f"|variance| >= 2.5%", delta_color="inverse")
    col2.metric("Monitor Closely", f"{yellow_count} projects", delta=f"|variance| 0.5–2.5%", delta_color="inverse")
    col3.metric("On Track", f"{green_count} projects")

    sort_col, filter_col = st.columns([1, 1])
    with sort_col:
        sort_order = st.selectbox(
            "Sort by variance",
            options=["Highest to Lowest", "Lowest to Highest", "Red first"],
            key="alerts_sort",
        )
    with filter_col:
        status_filter = st.selectbox(
            "Filter by status",
            options=["All", "Red only", "Yellow only", "Green only"],
            key="alerts_filter",
        )

    if sort_order == "Highest to Lowest":
        sorted_df = df.sort_values("variance_pct", ascending=False)
    elif sort_order == "Lowest to Highest":
        sorted_df = df.sort_values("variance_pct", ascending=True)
    else:
        sorted_df = df.assign(_abs=df["variance_pct"].abs()).sort_values("_abs", ascending=False).drop(columns="_abs")

    for _, row in sorted_df.iterrows():
        status, color, label, action = _classify(row)

        if status_filter == "Red only" and label != "RED":
            continue
        if status_filter == "Yellow only" and label != "YELLOW":
            continue
        if status_filter == "Green only" and label != "GREEN":
            continue
        variance_str = f"+{row['variance_pct']*100:.1f}%" if row["variance_pct"] > 0 else f"{row['variance_pct']*100:.1f}%"

        st.markdown(
            f"""
            <div style="
                border-left: 5px solid {color};
                background-color: #FAFAFA;
                padding: 1rem 1.2rem;
                margin-bottom: 0.75rem;
                border-radius: 0 4px 4px 0;
            ">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem;">
                    <span style="font-weight:700; color:{PREG_NAVY}; font-size:1rem;">
                        {row['project_name']}
                    </span>
                    <span style="
                        background-color:{color};
                        color:{WHITE};
                        font-size:0.7rem;
                        font-weight:700;
                        letter-spacing:0.1em;
                        padding:0.2rem 0.6rem;
                        border-radius:3px;
                    ">{label}</span>
                </div>
                <div style="color:#555; font-size:0.85rem; margin-bottom:0.4rem;">
                    {row['city']}, {row['state']} &nbsp;|&nbsp; {row['asset_type']} &nbsp;|&nbsp;
                    Variance: <strong>{variance_str}</strong> &nbsp;|&nbsp;
                    Spent: ${row['actual_spend']:,.0f} of ${row['original_budget']:,.0f} budget &nbsp;|&nbsp;
                    {int(row['change_orders_count'])} CO(s)
                </div>
                <div style="color:#333; font-size:0.88rem;">
                    <strong>Recommended Action:</strong> {action}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
