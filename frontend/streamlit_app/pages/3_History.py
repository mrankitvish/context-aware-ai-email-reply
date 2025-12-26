import streamlit as st
from api_client import APIClient
from utils import init_page
import pandas as pd

init_page("History")

st.title("📜 History")

try:
    threads = APIClient.list_threads(limit=100)
    
    if not threads:
        st.info("No history available yet.")
    else:
        # Prepare data for table
        data = []
        for thread in threads:
            for email in thread['emails']:
                has_reply = email.get('reply') is not None
                data.append({
                    "Date": email['received_at'][:10],
                    "Time": email['received_at'][11:19],
                    "Sender": email['sender'],
                    "Subject": email['subject'],
                    "Status": "✅ Replied" if has_reply else "⏳ Pending",
                    "Thread ID": thread['id'],
                    "Email ID": email['id']
                })
        
        df = pd.DataFrame(data)
        
        # Filters
        st.markdown("### Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Status", ["All", "✅ Replied", "⏳ Pending"])
        with col2:
            search_sender = st.text_input("Search Sender", placeholder="Enter sender email...")
        with col3:
            search_subject = st.text_input("Search Subject", placeholder="Enter subject...")
        
        # Apply filters
        filtered_df = df.copy()
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df["Status"] == status_filter]
        if search_sender:
            filtered_df = filtered_df[filtered_df["Sender"].str.contains(search_sender, case=False, na=False)]
        if search_subject:
            filtered_df = filtered_df[filtered_df["Subject"].str.contains(search_subject, case=False, na=False)]
        
        st.markdown("---")
        st.markdown(f"### Results ({len(filtered_df)} emails)")
        
        # Display table
        if len(filtered_df) == 0:
            st.info("No emails match your filters.")
        else:
            # Display with action buttons
            for idx, row in filtered_df.iterrows():
                with st.container(border=True):
                    c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 3, 2, 1, 1])
                    
                    c1.write(row['Date'])
                    c2.write(row['Sender'])
                    c3.write(row['Subject'])
                    c4.write(row['Status'])
                    
                    if c5.button("View", key=f"view_{row['Email ID']}"):
                        # Fetch and display email details
                        try:
                            summary = APIClient.get_email_summary(row['Email ID'])
                            st.session_state[f"view_email_{row['Email ID']}"] = summary
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    
                    if c6.button("Close", key=f"close_btn_{row['Email ID']}", disabled=not st.session_state.get(f"view_email_{row['Email ID']}")):
                        if f"view_email_{row['Email ID']}" in st.session_state:
                            del st.session_state[f"view_email_{row['Email ID']}"]
                            st.rerun()
                
                # Show details if viewed
                if st.session_state.get(f"view_email_{row['Email ID']}"):
                    st.markdown("---")
                    summary_data = st.session_state[f"view_email_{row['Email ID']}"]["summary"]
                    
                    with st.expander("📊 Email Analysis", expanded=True):
                        # Key Metrics
                        st.markdown("#### Key Metrics")
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.metric(
                                "Intent", 
                                summary_data.get('classification', {}).get('intent', 'Unknown'),
                                help=f"Confidence: {summary_data.get('classification', {}).get('confidence', 0):.0%}"
                            )
                        with m2:
                            sentiment = summary_data.get('sentiment', {})
                            st.metric(
                                "Sentiment", 
                                sentiment.get('label', 'Unknown'),
                                help=f"Score: {sentiment.get('score', 0):.2f} | Tone: {sentiment.get('tone', 'N/A')}"
                            )
                        with m3:
                            urgency = summary_data.get('urgency', {})
                            st.metric(
                                "Urgency", 
                                urgency.get('level', 'Unknown'),
                                help=f"Response time: {urgency.get('suggested_response_time', 'N/A')}"
                            )
                        
                        # Content Analysis
                        st.markdown("#### Content Analysis")
                        ca = summary_data.get('content_analysis', {})
                        
                        st.info(f"**Main Topic:** {ca.get('main_topic', 'N/A')}")
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if ca.get('questions'):
                                st.markdown("**Questions to Address:**")
                                for q in ca['questions']:
                                    st.markdown(f"• {q}")
                            else:
                                st.caption("No questions identified")
                        
                        with col_b:
                            if ca.get('action_items'):
                                st.markdown("**Action Items:**")
                                for item in ca['action_items']:
                                    st.markdown(f"• {item}")
                            else:
                                st.caption("No action items identified")
                        
                        # Additional Context
                        if ca.get('mentioned_entities') or ca.get('dates_deadlines'):
                            st.markdown("#### Additional Context")
                            
                            if ca.get('mentioned_entities'):
                                st.markdown(f"**Entities:** {', '.join(ca['mentioned_entities'])}")
                            
                            if ca.get('dates_deadlines'):
                                st.markdown(f"**Dates/Deadlines:** {', '.join(ca['dates_deadlines'])}")
                        
                        # Recommended Tone
                        st.markdown("#### AI Recommendation")
                        st.success(f"**Recommended Tone:** {summary_data.get('recommended_tone', 'Professional')}")
                        
                        if urgency.get('reason'):
                            st.caption(f"💡 {urgency['reason']}")


except Exception as e:
    st.error(f"Failed to load history: {str(e)}")
    st.warning("Make sure the backend server is running!")
