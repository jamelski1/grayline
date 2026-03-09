"""Grayline — Strategic Monitoring & Analytics Platform.

Main Streamlit application entry point.
Run with: streamlit run app/main.py
"""

import sys
from pathlib import Path

# Ensure src/ is on the path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st

from grayline.dashboard.layout import apply_global_style
from grayline.pipelines.build_weekly_panel import load_panel
from grayline.utils.logging import setup_logging

setup_logging()

st.set_page_config(
    page_title="Grayline — Strategic Monitoring",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_style()

# Sidebar navigation
st.sidebar.markdown("### ◆ GRAYLINE")
st.sidebar.caption("Strategic Monitoring & Analytics")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    options=[
        "Executive Summary",
        "Inputs",
        "Intermediate Effects",
        "Outcomes",
        "Regression Analysis",
        "Data Quality",
    ],
    label_visibility="collapsed",
)

st.sidebar.divider()
if st.sidebar.button("⟳ Rebuild Data Panel"):
    from grayline.pipelines.build_weekly_panel import build_panel

    with st.spinner("Rebuilding weekly panel..."):
        build_panel()
    st.rerun()

st.sidebar.caption("v0.1.0 · Sample Data Mode")


# Load data once and cache
@st.cache_data(ttl=300)
def get_panel():
    return load_panel()


panel = get_panel()

# Route to selected page
if page == "Executive Summary":
    from pages.executive_summary import render

    render(panel)
elif page == "Inputs":
    from pages.inputs import render

    render(panel)
elif page == "Intermediate Effects":
    from pages.intermediate_effects import render

    render(panel)
elif page == "Outcomes":
    from pages.outcomes import render

    render(panel)
elif page == "Regression Analysis":
    from pages.regression_analysis import render

    render(panel)
elif page == "Data Quality":
    from pages.data_quality import render

    render(panel)
