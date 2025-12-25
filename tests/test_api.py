import pytest
from unittest.mock import MagicMock, patch

# Mock the LLM to avoid real API calls during tests
# We'll patch the EmailProcessor and ReplyGenerator classes or their internal LLMs

@pytest.fixture
def mock_llm_response():
    with patch("backend.ai.email_processor.ChatOpenAI") as mock_chat:
        # Mock for EmailProcessor
        mock_instance = mock_chat.return_value
        # Mock the chain invocation
        # The processor uses a chain: prompt | llm | parser
        # It's easier to mock the `_generate_summary` method of EmailProcessor directly
        # or mock the chain execution.
        # Let's mock EmailProcessor._generate_summary for simplicity in integration tests
        # unless we want to test the prompt construction too.
        yield mock_chat

def test_submit_email_success(client):
    # We need to mock the EmailProcessor.process_email or the LLM inside it.
    # Since we want to test the API, mocking the heavy AI part is acceptable.
    
    with patch("backend.ai.email_processor.EmailProcessor.process_email") as mock_process:
        # Setup mock return value
        mock_summary = MagicMock()
        mock_summary.email_id = "test-email-id"
        mock_summary.summary_json = {
            "email_id": "test-email-id",
            "thread_info": {"thread_id": "test-thread-id"}
        }
        mock_process.return_value = mock_summary

        response = client.post("/api/v1/email/submit", json={
            "subject": "Test Subject",
            "body": "Test Body",
            "sender": "test@example.com"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["email_id"] == "test-email-id"

def test_submit_email_unsafe_content(client):
    response = client.post("/api/v1/email/submit", json={
        "subject": "Lottery Winner",
        "body": "You have won a lottery! Send money.",
        "sender": "scammer@example.com"
    })
    
    assert response.status_code == 400
    assert "unsafe keyword" in response.json()["detail"]

def test_get_email_summary_not_found(client):
    response = client.get("/api/v1/email/non-existent-id/summary")
    assert response.status_code == 404

def test_list_threads_empty(client):
    response = client.get("/api/v1/threads/")
    assert response.status_code == 200
    assert response.json() == []

def test_generate_reply_success(client, db_session):
    # First, insert a dummy EmailSummary into the DB manually
    from backend.db.models import EmailSummary, Email, Thread
    import json
    
    thread = Thread(id="t1")
    email = Email(id="e1", thread_id="t1", sender="s", subject="sub", body="b")
    summary = EmailSummary(
        email_id="e1",
        summary_json={
            "thread_info": {"thread_id": "t1"},
            "classification": {"intent": "test"},
            "sentiment": {"label": "neutral"},
            "urgency": {"level": "low"},
            "content_analysis": {"main_topic": "topic", "questions": [], "action_items": []}
        }
    )
    db_session.add(thread)
    db_session.add(email)
    db_session.add(summary)
    db_session.commit()

    # Mock ReplyGenerator.generate
    with patch("backend.ai.reply_generator.ReplyGenerator.generate") as mock_generate:
        mock_generate.return_value = {
            "status": "success",
            "reply": "This is a generated reply."
        }
        
        response = client.post("/api/v1/email/e1/generate-reply", json={
            "tone": "professional",
            "auto_send": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "This is a generated reply."
        assert data["email_id"] == "e1"

def test_generate_reply_unsafe_tone(client, db_session):
    # Insert dummy data
    from backend.db.models import EmailSummary, Email, Thread
    thread = Thread(id="t1")
    email = Email(id="e1", thread_id="t1", sender="s", subject="sub", body="b")
    summary = EmailSummary(
        email_id="e1",
        summary_json={"thread_info": {"thread_id": "t1"}}
    )
    db_session.add(thread)
    db_session.add(email)
    db_session.add(summary)
    db_session.commit()

    # Mock ReplyGenerator.generate to return error
    with patch("backend.ai.reply_generator.ReplyGenerator.generate") as mock_generate:
        mock_generate.return_value = {
            "status": "error",
            "error": "Safety violation",
            "reply": "Unsafe content"
        }
        
        response = client.post("/api/v1/email/e1/generate-reply", json={
            "tone": "unsafe",
            "auto_send": False
        })
        
        assert response.status_code == 400
        assert "Safety violation" in response.json()["detail"]
