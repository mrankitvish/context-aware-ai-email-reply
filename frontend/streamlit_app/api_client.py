import requests
import os
from typing import Optional, Dict, Any

# Default to localhost:8000 if not set
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

class APIClient:
    @staticmethod
    def _handle_response(response: requests.Response) -> Any:
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_detail = response.json().get("detail", str(e))
            except:
                error_detail = str(e)
            raise Exception(f"API Error: {error_detail}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    @staticmethod
    def process_raw_email(raw_content: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """Process raw email content via webhook"""
        url = f"{API_BASE_URL}/email/webhook"
        payload = {
            "raw_content": raw_content,
            "thread_id": thread_id
        }
        response = requests.post(url, json=payload)
        return APIClient._handle_response(response)

    @staticmethod
    def submit_email(subject: str, body: str, sender: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        url = f"{API_BASE_URL}/email/submit"
        payload = {
            "subject": subject,
            "body": body,
            "sender": sender,
            "thread_id": thread_id
        }
        response = requests.post(url, json=payload)
        return APIClient._handle_response(response)

    @staticmethod
    def get_email_summary(email_id: str) -> Dict[str, Any]:
        url = f"{API_BASE_URL}/email/{email_id}/summary"
        response = requests.get(url)
        return APIClient._handle_response(response)

    @staticmethod
    def generate_reply(email_id: str, tone: str = "professional", auto_send: bool = False, instructions: Optional[str] = None) -> Dict[str, Any]:
        url = f"{API_BASE_URL}/email/{email_id}/generate-reply"
        payload = {
            "tone": tone,
            "auto_send": auto_send,
            "instructions": instructions
        }
        response = requests.post(url, json=payload)
        return APIClient._handle_response(response)

    @staticmethod
    def list_threads(skip: int = 0, limit: int = 100) -> list:
        url = f"{API_BASE_URL}/threads/"
        params = {"skip": skip, "limit": limit}
        response = requests.get(url, params=params)
        return APIClient._handle_response(response)

    @staticmethod
    def get_thread(thread_id: str) -> Dict[str, Any]:
        url = f"{API_BASE_URL}/threads/{thread_id}"
        response = requests.get(url)
        return APIClient._handle_response(response)
