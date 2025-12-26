import streamlit as st
from api_client import APIClient
from utils import init_page

init_page("Email Threads")

st.title("📨 Email Threads")

try:
    threads = APIClient.list_threads(limit=50)
    
    if not threads:
        st.info("No email threads found. Start by submitting a new email!")
    else:
        # Search/Filter
        search = st.text_input("🔍 Search threads", placeholder="Search by subject or sender...")
        
        st.markdown("---")
        
        for thread in threads:
            last_email = thread['emails'][-1] if thread['emails'] else None
            if not last_email:
                continue
            
            # Apply search filter
            if search:
                if search.lower() not in last_email['subject'].lower() and search.lower() not in last_email['sender'].lower():
                    continue
            
            # Thread Card
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Header
                    has_reply = any(e.get('reply') for e in thread['emails'])
                    status_badge = "✅ Replied" if has_reply else "⏳ Pending"
                    st.markdown(f"**{last_email['subject']}** {status_badge}")
                    
                    # Meta info
                    st.caption(f"From: {last_email['sender']} | Date: {thread['created_at'][:10]} | Emails: {len(thread['emails'])}")
                    
                    # Preview
                    preview = last_email['body'][:150] + "..." if len(last_email['body']) > 150 else last_email['body']
                    st.text(preview)
                
                with col2:
                    if st.button("View Details", key=f"view_{thread['id']}", use_container_width=True):
                        # Show thread details in expander
                        st.session_state[f"show_thread_{thread['id']}"] = True
                        st.rerun()
                
                # Thread Details (if expanded)
                if st.session_state.get(f"show_thread_{thread['id']}", False):
                    st.markdown("---")
                    st.markdown("#### Thread History")
                    
                    for idx, email in enumerate(thread['emails']):
                        with st.expander(f"Email {idx + 1}: {email['subject']}", expanded=(idx == len(thread['emails']) - 1)):
                            st.markdown(f"**From:** {email['sender']}")
                            st.markdown(f"**Date:** {email['received_at']}")
                            st.markdown(f"**Subject:** {email['subject']}")
                            st.markdown("**Body:**")
                            st.text_area("", value=email['body'], height=150, disabled=True, key=f"body_{email['id']}")
                            
                            if email.get('reply'):
                                st.success("**Generated Reply:**")
                                st.text_area("", value=email['reply']['reply_text'], height=150, disabled=True, key=f"reply_{email['id']}")
                                st.caption(f"Tone: {email['reply']['tone']}")
                    
                    if st.button("Close Details", key=f"close_{thread['id']}"):
                        st.session_state[f"show_thread_{thread['id']}"] = False
                        st.rerun()

except Exception as e:
    st.error(f"Failed to load threads: {str(e)}")
    st.warning("Make sure the backend server is running!")
