# How-to Guide

This guide provides detailed instructions on how to use the Context Aware AI Email Reply API.

## Table of Contents

1. [Submitting an Email](#1-submitting-an-email)
2. [Retrieving a Summary](#2-retrieving-a-summary)
3. [Generating a Reply](#3-generating-a-reply)
4. [Managing Threads](#4-managing-threads)
5. [Handling Errors](#5-handling-errors)

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

## 5. Handling Errors

The API uses standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid input or Safety Violation (Guardrail triggered)
- `404 Not Found`: Resource (email/thread) not found
- `422 Validation Error`: Request body does not match schema
- `500 Internal Server Error`: Server-side processing error
