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

def section_banner(label: str, title: str) -> None:
    import streamlit as st
    st.markdown(
        f"""
        <div class="preg-section-banner">
            <div class="preg-section-label">{label}</div>
            <div class="preg-section-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def inject_css() -> str:
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Montserrat', sans-serif;
        }}
        .preg-topbar {{
            background-color: {PREG_NAVY};
            color: {WHITE};
            font-family: 'Montserrat', sans-serif;
            font-size: 0.75rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            padding: 0.45rem 2rem;
            margin-bottom: 0;
        }}
        .preg-header {{
            background-color: {WHITE};
            padding: 1.2rem 2rem;
            border-bottom: 1px solid #DEE2E6;
            margin-bottom: 1rem;
        }}
        .preg-logo {{
            height: 80px;
            width: auto;
            display: block;
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
        .preg-section-banner {{
            background-color: {PREG_NAVY};
            padding: 1.6rem 2rem;
            margin: 0.5rem 0 1.2rem 0;
        }}
        .preg-section-label {{
            color: #8FA8C0;
            font-family: 'Montserrat', sans-serif;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }}
        .preg-section-title {{
            color: {WHITE};
            font-family: 'Cormorant Garamond', serif;
            font-size: 2rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            line-height: 1.2;
        }}
    </style>
    """
