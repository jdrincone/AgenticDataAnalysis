"""
Header component for the application.
"""
import streamlit as st
from src.config.settings import config

def render_header():
    """Render the application header."""
    st.markdown(f"""
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 2rem;'>
            <h1 style='font-size: 3rem; font-weight: 800; color: {config.PRIMARY_COLOR}; margin-bottom: 0.2em;'>
                🤖 {config.APP_NAME}
            </h1>
            <p style='font-size: 1.3rem; color: #444; margin-top: 0;'>
                {config.APP_DESCRIPTION}
            </p>
        </div>
    """, unsafe_allow_html=True) 