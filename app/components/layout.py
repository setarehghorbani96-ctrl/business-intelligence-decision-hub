"""Layout helpers for the Streamlit executive dashboard."""

from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    """Apply a lightweight enterprise visual treatment."""
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(21, 94, 239, 0.08), transparent 28%),
                    linear-gradient(180deg, #f8fafc 0%, #eef4ff 100%);
            }
            h1,
            h2,
            h3 {
                color: #0f172a;
            }
            [data-testid="stSidebar"] {
                background: #f8fafc;
            }
            .hero-panel {
                padding: 1.4rem 1.6rem;
                border: 1px solid rgba(21, 94, 239, 0.12);
                border-radius: 18px;
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(238, 244, 255, 0.98));
                box-shadow: 0 14px 32px rgba(15, 23, 42, 0.06);
                margin-bottom: 0.8rem;
            }
            .hero-kicker {
                color: #155eef;
                font-size: 0.82rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.45rem;
            }
            .hero-title {
                font-size: 2.1rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 0.25rem;
            }
            .hero-subtitle {
                font-size: 1.05rem;
                color: #0f172a;
                margin-bottom: 0.5rem;
            }
            .hero-description {
                color: #475467;
                margin-bottom: 0;
            }
            .dashboard-section {
                margin-top: 1.25rem;
                margin-bottom: 0.65rem;
            }
            .dashboard-section h2 {
                margin-bottom: 0.1rem;
                font-size: 1.35rem;
            }
            .dashboard-section p {
                color: #475467;
                margin-bottom: 0;
            }
            .metric-card {
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 16px;
                padding: 0.9rem 1rem;
                background: rgba(255, 255, 255, 0.94);
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
                min-height: 116px;
            }
            .metric-card-label {
                color: #475467;
                font-size: 0.85rem;
                margin-bottom: 0.35rem;
            }
            .metric-card-value {
                color: #0f172a;
                font-size: 1.5rem;
                font-weight: 700;
                line-height: 1.2;
            }
            .metric-card-helper {
                color: #667085;
                font-size: 0.78rem;
                margin-top: 0.4rem;
            }
            .insight-card {
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-left: 4px solid #155eef;
                border-radius: 14px;
                padding: 0.95rem 1rem;
                background: rgba(255, 255, 255, 0.96);
                margin-bottom: 0.7rem;
            }
            .insight-title {
                color: #0f172a;
                font-weight: 600;
                margin-bottom: 0.25rem;
            }
            .insight-body {
                color: #475467;
                margin: 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str, description: str) -> None:
    """Render the page title block."""
    st.markdown(
        (
            '<div class="hero-panel">'
            '<div class="hero-kicker">Executive Decision Support</div>'
            f'<div class="hero-title">{title}</div>'
            f'<div class="hero-subtitle">{subtitle}</div>'
            f'<p class="hero-description">{description}</p>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_section_header(title: str, description: str) -> None:
    """Render a section title and supporting description."""
    st.markdown(
        (
            '<div class="dashboard-section">'
            f"<h2>{title}</h2>"
            f"<p>{description}</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_highlight_box(title: str, body: str) -> None:
    """Render a compact callout box for dashboard insights."""
    st.markdown(
        (
            '<div class="insight-card">'
            f'<div class="insight-title">{title}</div>'
            f'<p class="insight-body">{body}</p>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, message: str) -> None:
    """Render a helpful empty-state message."""
    st.warning(title)
    st.info(message)
