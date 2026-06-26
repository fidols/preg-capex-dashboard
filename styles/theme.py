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
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Montserrat', sans-serif;
        }}
        .preg-header {{
            background-color: {PREG_NAVY};
            padding: 1.6rem 2rem;
            border-bottom: 4px solid {PREG_BLUE};
            margin-bottom: 1rem;
        }}
        .preg-logo {{
            height: 70px;
            width: auto;
            display: block;
            filter: brightness(0) invert(1);
            margin-bottom: 0.3rem;
        }}
        .preg-header p {{
            color: #BDC3C7;
            font-family: 'Montserrat', sans-serif;
            font-size: 0.82rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin: 0.4rem 0 0 0;
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
