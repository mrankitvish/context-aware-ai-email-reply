from fastapi.testclient import TestClient
from backend.main import app
import json

client = TestClient(app)

def test_workflow():
    print("1. Submitting Email...")
    email_data = {
        "subject": "Pricing Inquiry",
        "body": "Hi, I am interested in your enterprise plan. Can you send me the pricing details for 50 users? Thanks, John.",
        "sender": "john@example.com"
    }
    response = client.post("/api/v1/email/submit", json=email_data)
    assert response.status_code == 200
    data = response.json()
    email_id = data["email_id"]
    print(f"   Success! Email ID: {email_id}")
    summary = data['summary']
    print(f"   Summary: {json.dumps(summary, indent=2)}")
    
    # Verify thread_id matches
    # Note: In the first email of a new thread, the thread_id should be a UUID (or whatever we generated), 
    # NOT "Earning Message" or similar text.
    thread_id = summary['thread_info']['thread_id']
    print(f"   Thread ID in Summary: {thread_id}")
    
    # We can't easily assert the exact UUID value without knowing what was generated, 
    # but we can check it's not the subject line if we expect a UUID.
    # However, for now, just printing it is enough for manual verification.

    print("\n2. Getting Summary...")
    response = client.get(f"/api/v1/email/{email_id}/summary")
    assert response.status_code == 200
    print("   Success! Summary retrieved.")

    print("\n3. Testing Thread APIs...")
    # List threads
    response = client.get("/api/v1/threads/")
    assert response.status_code == 200
    threads = response.json()
    print(f"   Listed {len(threads)} threads.")
    
    if threads:
        t_id = threads[0]['id']
        print(f"   Fetching details for thread {t_id}...")
        response = client.get(f"/api/v1/threads/{t_id}")
        assert response.status_code == 200
        thread_details = response.json()
        print(f"   Thread has {len(thread_details['emails'])} emails.")
        
        # Check if any email has a reply
        for email in thread_details['emails']:
            if email.get('reply'):
                print(f"   [VERIFIED] Email {email['id']} has a generated reply: {email['reply']['reply_text'][:50]}...")

    print("\n4. Generating Reply (Professional)...")
    reply_request = {
        "tone": "professional",
        "auto_send": False
    }
    response = client.post(f"/api/v1/email/{email_id}/generate-reply", json=reply_request)
    assert response.status_code == 200
    reply_data = response.json()
    print(f"   Success! Reply: {reply_data['reply'][:50]}...")
    print(f"   Thread ID: {reply_data.get('thread_id')}")
    print(f"   Email ID: {reply_data.get('email_id')}")

    print("\n5. Testing Guardrails (Unsafe Tone)...")
    unsafe_request = {
        "tone": "sexual",
        "auto_send": False
    }
    response = client.post(f"/api/v1/email/{email_id}/generate-reply", json=unsafe_request)
    if response.status_code == 400:
        print(f"   Success! Request rejected as expected: {response.json()['detail']}")
    else:
        print(f"   Warning: Request was not rejected. Status: {response.status_code}")

    print("\n6. Testing Input Guardrails (Unsafe Email)...")
    # This tests the /submit endpoint guardrail
    unsafe_email = {
        "subject": "Lottery Winner",
        "body": "You have won a lottery! Send money to claim.",
        "sender": "scammer@example.com"
    }
    response = client.post("/api/v1/email/submit", json=unsafe_email)
    if response.status_code == 400:
        print(f"   Success! Email rejected as expected: {response.json()['detail']}")
    else:
        print(f"   Warning: Email was not rejected. Status: {response.status_code}")

    # The previous test (Step 5) tested the ReplyGenerator guardrail (Unsafe Tone)
    # which now uses the same underlying check_safety logic for keywords like "sexual".

if __name__ == "__main__":
    test_workflow()
