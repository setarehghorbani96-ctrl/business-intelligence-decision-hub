"""Minimal Streamlit application for the repository foundation."""

import streamlit as st

st.set_page_config(
    page_title="Business Intelligence Decision Hub",
    layout="wide",
)

st.title("Business Intelligence Decision Hub")
st.write(
    "A professional portfolio project for NovaEnergy Services focused on "
    "enterprise decision support, KPI visibility, and future scenario analysis."
)

st.subheader("Current Status")
st.info("Project foundation initialized")

st.subheader("Planned Modules")
st.markdown(
    """
    - Synthetic enterprise data generation
    - Python ETL pipeline
    - PostgreSQL analytics layer
    - FastAPI business services
    - Streamlit executive dashboard
    - AI-style insight engine
    - Scenario analysis workflows
    - Power BI documentation assets
    """
)

