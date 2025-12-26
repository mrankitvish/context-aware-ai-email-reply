import streamlit as st
from api_client import APIClient
from utils import init_page

init_page("Submit Email")

# Initialize Session State
if "email_data" not in st.session_state:
    st.session_state.email_data = None
if "form_sender" not in st.session_state:
    st.session_state.form_sender = ""
if "form_subject" not in st.session_state:
    st.session_state.form_subject = ""
if "form_body" not in st.session_state:
    st.session_state.form_body = ""

st.title("📧 Submit Email")

# Compose / Input Section
col1, col_or, col2 = st.columns([10, 1, 10])

with col1:
    with st.container(border=True):
        st.markdown("### Form Input")
        sender = st.text_input("From", value=st.session_state.form_sender, placeholder="client@example.com")
        subject = st.text_input("Subject", value=st.session_state.form_subject, placeholder="Meeting Request")
        body = st.text_area("Body", value=st.session_state.form_body, height=150, placeholder="Email content...")
        
        if st.button("Submit", type="primary", use_container_width=True):
            if not sender or not subject or not body:
                st.error("Please fill in all fields")
            else:
                with st.spinner("Analyzing..."):
                    try:
                        res = APIClient.submit_email(sender, subject, body)
                        st.session_state.email_data = {
                            "email_id": res['email_id'],
                            "summary": res['summary'],
                            "reply": None, 
                            "thread_id": None 
                        }
                        st.success("Email submitted successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")

with col_or:
    st.markdown("<div style='text-align: center; margin-top: 100px;'>OR</div>", unsafe_allow_html=True)

with col2:
    with st.container(border=True):
        st.markdown("### Paste Email")
        paste_text = st.text_area("Paste raw email text", height=285, placeholder="Paste raw email text here...")
        if st.button("Process Paste", use_container_width=True):
            if paste_text:
                lines = paste_text.split('\n')
                p_subject = lines[0] if lines else "No Subject"
                p_body = paste_text
                p_sender = "unknown@example.com"
                
                st.session_state.form_sender = p_sender
                st.session_state.form_subject = p_subject
                st.session_state.form_body = p_body
                st.rerun()

# Analysis & Reply Section
if st.session_state.email_data:
    st.markdown("---")
    
    # Summary
    if st.session_state.email_data.get('summary'):
        summary = st.session_state.email_data['summary']
        with st.expander("📊 Analysis Summary", expanded=True):
            sc1, sc2, sc3 = st.columns(3)
            with sc1: st.metric("Intent", summary.get('classification', {}).get('intent', 'Unknown'))
            with sc2: st.metric("Sentiment", summary.get('sentiment', {}).get('label', 'Unknown'))
            with sc3: st.metric("Urgency", summary.get('urgency', {}).get('level', 'Unknown'))
            
            st.markdown("#### Key Insights")
            ca = summary.get('content_analysis', {})
            st.info(f"**Main Topic:** {ca.get('main_topic', 'N/A')}")
            
            if ca.get('questions'):
                st.markdown("**Questions:**")
                for q in ca['questions']: st.markdown(f"- {q}")
            if ca.get('action_items'):
                st.markdown("**Action Items:**")
                for item in ca['action_items']: st.markdown(f"- {item}")

    # Reply
    st.markdown("### Generated Reply")
    reply_data = st.session_state.email_data.get('reply')
    reply_text = reply_data['reply_text'] if reply_data else ""
    
    st.text_area("Draft", value=reply_text, height=300, placeholder="Click 'Generate Reply' to create a draft.", key="draft_area")
    
    # Actions
    st.markdown("#### Actions")
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 6, 2])
        with c1:
            tone = st.selectbox("Tone", ["professional", "friendly", "urgent", "assertive"])
        with c2:
            instructions = st.text_input("Instructions", placeholder="Type any additional instruction...")
        with c3:
            btn_label = "🔄 Regenerate" if reply_text else "✨ Generate Reply"
            if st.button(btn_label, type="primary", use_container_width=True):
                if st.session_state.email_data.get('email_id'):
                    with st.spinner("Generating..."):
                        try:
                            new_reply = APIClient.generate_reply(
                                st.session_state.email_data['email_id'],
                                tone=tone,
                                instructions=instructions
                            )
                            st.session_state.email_data['reply'] = {
                                "reply_text": new_reply['reply'],
                                "tone": tone
                            }
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
