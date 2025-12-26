# How-to Guide

This guide provides detailed instructions on how to use the Context Aware AI Email Reply API.

## Table of Contents

1. [Submitting an Email](#1-submitting-an-email)
2. [Retrieving a Summary](#2-retrieving-a-summary)
3. [Generating a Reply](#3-generating-a-reply)
4. [Managing Threads](#4-managing-threads)
5. [Processing Raw Email via Webhook](#5-processing-raw-email-via-webhook)
6. [Handling Errors](#6-handling-errors)

---

## 1. Submitting an Email

To process an incoming email, send a POST request to `/api/v1/email/submit`.

**Endpoint:** `POST /api/v1/email/submit`

**Request Body:**

```json
{
  "subject": "Project Deadline Extension",
  "body": "Hi Team, due to unforeseen circumstances, we need to extend the deadline by 2 days.",
  "sender": "manager@example.com",
  "thread_id": "optional-thread-uuid"
}
```

_Note: `thread_id` is optional. If provided, the email is added to that thread. If not, a new thread is created or matched based on headers (future feature)._

**Response:**

```json
{
  "status": "success",
  "email_id": "generated-email-uuid",
  "summary": {
    "email_id": "generated-email-uuid",
    "timestamp": "2025-12-25 10:00:00",
    "sender": { "email": "manager@example.com" },
    "classification": {
      "intent": "Request",
      "sub_intent": "Deadline Extension"
    },
    "sentiment": { "score": 0.2, "label": "Neutral" },
    "urgency": { "level": "Medium" }
    // ... other summary fields
  }
}
```

## 2. Retrieving a Summary

You can retrieve the AI-generated summary of any email using its ID.

**Endpoint:** `GET /api/v1/email/{email_id}/summary`

**Response:**
Returns the JSON summary object generated during submission.

## 3. Generating a Reply

Generate a context-aware reply for a specific email.

**Endpoint:** `POST /api/v1/email/{email_id}/generate-reply`

**Request Body:**

```json
{
  "tone": "professional",
  "auto_send": false
}
```

_Supported tones: "professional", "friendly", "formal", "concise", etc._

**Response:**

```json
{
  "email_id": "email-uuid",
  "thread_id": "thread-uuid",
  "reply": "Subject: Re: Project Deadline Extension\n\nHi [Name],\n\nThank you for the update. We have noted the deadline extension..."
}
```

**Guardrails:**
If the requested tone is inappropriate (e.g., "sexual", "hateful") or the generated content violates safety policies, the API will return a `400 Bad Request` error.

## 4. Managing Threads

### List All Threads

**Endpoint:** `GET /api/v1/threads/`
_Query Params:_ `skip` (default 0), `limit` (default 100)

### Get Thread Details

**Endpoint:** `GET /api/v1/threads/{thread_id}`

Returns the full conversation history, including all emails and their generated replies.

## 5. Processing Raw Email via Webhook

**NEW**: Process raw email content with AI-powered parsing and safety guardrails.

**Endpoint:** `POST /api/v1/email/webhook`

This endpoint is ideal for:

- Integrating with email clients (Gmail, Outlook)
- Automation workflows (Zapier, Make.com, n8n)
- Processing pasted email content
- Email forwarding services

**Request Body:**

```json
{
  "raw_content": "From: john.doe@example.com\nSubject: Project Update\n\nHi Team,\n\nI wanted to schedule a meeting...",
  "thread_id": "optional-thread-uuid"
}
```

**How it works:**

1. **LLM-Powered Parsing**: AI extracts sender, subject, and body from various formats
2. **Safety Guardrails**: Content is checked for scams, phishing, explicit content, etc.
3. **Email Analysis**: Full analysis (intent, sentiment, urgency, action items)
4. **Storage**: Email and analysis are stored for future reference

**Response:**

```json
{
  "status": "success",
  "email_id": "generated-uuid",
  "summary": {
    "classification": { "intent": "request", "confidence": 0.95 },
    "sentiment": { "label": "Positive", "score": 0.8 },
    "urgency": { "level": "Medium", "suggested_response_time": "24 hours" },
    "content_analysis": {
      "main_topic": "Meeting scheduling",
      "questions": ["Are you available next Tuesday?"],
      "action_items": ["Schedule meeting"]
    }
  },
  "parsed_data": {
    "sender": "john.doe@example.com",
    "subject": "Project Update",
    "body_preview": "Hi Team,\n\nI wanted to schedule..."
  }
}
```

**Example - Plain Text Email:**

```bash
curl -X POST http://localhost:8000/api/v1/email/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "raw_content": "Hey, can we reschedule to Friday? Something urgent came up."
  }'
```

**Safety Features:**

- AI checks content against comprehensive safety rules during parsing
- Post-processing validation against unsafe keywords
- Automatic rejection of scams, phishing, explicit content, malware indicators

For detailed webhook documentation, see [WEBHOOK_API.md](WEBHOOK_API.md).

## 6. Handling Errors

The API uses standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid input or Safety Violation (Guardrail triggered)
- `404 Not Found`: Resource (email/thread) not found
- `422 Validation Error`: Request body does not match schema
- `500 Internal Server Error`: Server-side processing error
