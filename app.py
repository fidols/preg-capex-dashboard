import streamlit as st
from data.projects import generate_projects
from components.kpi_strip import render_kpi_strip
from components.portfolio import render_portfolio_tab
from components.project_detail import render_project_detail_tab
from components.change_order import render_change_order_tab
from components.reporting import render_reporting_tab
from styles.theme import inject_css

st.set_page_config(
    page_title="Post Real Estate Group — CapEx Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(inject_css(), unsafe_allow_html=True)

st.markdown(
    """
    <div class="preg-topbar">
        CapEx Portfolio Dashboard &nbsp;·&nbsp; FY 2026 &nbsp;·&nbsp; 12 Active Projects
    </div>
    <div class="preg-header">
        <img src="https://postregroup.com/wp-content/uploads/2025/10/preg-logo.svg"
             alt="Post Real Estate Group"
             class="preg-logo" />
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
    "Portfolio Overview",
    "Project Detail",
    "Change Order Calculator",
    "Reporting",
])

with tab1:
    render_portfolio_tab(df)

with tab2:
    render_project_detail_tab(df)

with tab3:
    render_change_order_tab(df)

with tab4:
    render_reporting_tab(df)
