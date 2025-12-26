import streamlit as st
from utils import init_page

init_page("AI Email Reply")

st.title("🏠 AI Email Reply Tool")

st.markdown("""
## Welcome to the AI Email Reply Assistant

This tool helps you analyze emails and generate context-aware, professional replies using AI.

### Features

- **📧 Submit Email**: Compose or paste emails for analysis and reply generation
- **📨 Email Threads**: View and manage email conversation threads
- **📜 History**: Browse all processed emails with advanced filtering

### Getting Started

1. Navigate to **Submit Email** to process a new email
2. View the AI analysis including intent, sentiment, and urgency
3. Generate professional replies with customizable tone
4. Refine replies with additional instructions

### Quick Actions

Use the sidebar to navigate between different sections of the application.
""")

# Stats Dashboard
st.markdown("---")
st.markdown("### Quick Stats")

try:
    from api_client import APIClient
    threads = APIClient.list_threads(limit=100)
    
    total_threads = len(threads)
    total_emails = sum(len(t['emails']) for t in threads)
    replied_emails = sum(1 for t in threads for e in t['emails'] if e.get('reply'))
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Threads", total_threads)
    col2.metric("Total Emails", total_emails)
    col3.metric("Replied", replied_emails)
    
except Exception as e:
    st.info("Connect to backend to see statistics")
