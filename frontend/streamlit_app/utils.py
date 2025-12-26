import streamlit as st
import os

def load_css(file_path: str):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def init_page(page_title: str):
    st.set_page_config(
        page_title=f"{page_title} | AI Email Reply",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        load_css(css_path)
    
    # Sidebar - Streamlit auto-generates navigation from pages/
    # Just add branding
    with st.sidebar:
        st.markdown("---")
        st.caption("Context Aware AI Email Reply Tool")

