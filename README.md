# Context Aware AI Email Reply

## Problem

Businesses waste time manually replying to repetitive customer emails.

## Solution

This tool uses AI to generate professional, context-aware email replies in seconds. It analyzes email threads, understands context, and generates appropriate responses while ensuring safety through built-in guardrails.

## Documentation

- [**Quick Installation Guide**](docs/Quick-Installation-Guide.md): Get started in minutes.
- [**How-to Guide**](docs/How-to-Guide.md): Detailed API usage instructions.
- [**Advanced Configuration**](docs/Advanced-Configuration-Guide.md): LLM setup, Docker, and Helm configuration.

## Architecture

```mermaid
graph TD
    User[User / Client] -->|HTTP POST| API[FastAPI Server]
    API -->|Validate| Guardrail[Input Guardrail]
    Guardrail -- Unsafe --> Reject[400 Bad Request]
    Guardrail -- Safe --> DB[(PostgreSQL Database)]

    API -->|Process| Processor[Email Processor]
    Processor -->|Summarize| LLM["LLM (OpenAI/Local)"]
    LLM -->|Summary| DB

    API -->|Generate Reply| Generator[Reply Generator]
    Generator -->|Fetch Context| DB
    Generator -->|Draft| LLM
    LLM -->|Reply| Validator[Output Guardrail]
    Validator -- Unsafe --> RejectReply[Error]
    Validator -- Safe --> DB
    Validator -- Safe --> User
```

## Workflow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant DB
    participant LLM

    Client->>API: POST /submit (Email)
    API->>API: Input Guardrail Check
    alt Unsafe
        API-->>Client: 400 Bad Request
    else Safe
        API->>DB: Save Email
        API->>LLM: Generate Summary
        LLM-->>API: Summary JSON
        API->>DB: Save Summary
        API-->>Client: 200 OK (Email ID)
    end

    Client->>API: POST /generate-reply (Email ID)
    API->>DB: Fetch Email & Thread Context
    DB-->>API: Context
    API->>LLM: Generate Reply
    LLM-->>API: Draft Reply
    API->>API: Output Guardrail Check
    alt Unsafe
        API-->>Client: 400 Bad Request
    else Safe
        API->>DB: Save Reply
        API-->>Client: 200 OK (Reply)
    end
```

## Tech Stack

- **Python 3.11+**
- **FastAPI**: High-performance web framework.
- **PostgreSQL**: Database support.
- **LangChain & LangGraph**: Orchestrating AI workflows.
- **OpenAI API**: Powering the intelligence (configurable).

## Features

- **Context Awareness**: Analyzes full email threads to generate relevant replies.
- **Structured Summaries**: Extracts key info, intent, sentiment, and urgency.
- **Guardrails**: Prevents processing or generating unsafe/inappropriate content.
- **Thread Management**: Groups emails into conversation threads.
- **Configurable Tone**: Generate replies in Professional, Friendly, or other tones.

## Setup & Installation

1. **Clone the repository**

   ```bash
   git clone git@github.com:mrankitvish/context-aware-ai-email-reply.git
   cd context-aware-ai-email-reply
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4o  # Optional, default: gpt-4o
   OPENAI_BASE_URL=https://api.openai.com/v1  # Optional
   DATABASE_URL=postgresql://user:password@localhost:5432/emaildb
   ```

## Running the Application

Start the FastAPI server:

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Documentation

Access the interactive Swagger UI at `http://localhost:8000/docs`.

### Key Endpoints

- **Submit Email** (`POST /api/v1/email/submit`)

  - Submits a new email for processing.
  - Checks for unsafe content.
  - Returns an email ID and structured summary.

- **Get Summary** (`GET /api/v1/email/{email_id}/summary`)

  - Retrieves the analyzed summary of an email.

- **Generate Reply** (`POST /api/v1/email/{email_id}/generate-reply`)

  - Generates a reply based on the email context and requested tone.
  - Enforces safety guardrails on the generated output.

- **List Threads** (`GET /api/v1/threads/`)

  - Lists all email threads.

- **Get Thread** (`GET /api/v1/threads/{thread_id}`)
  - Retrieves full details of a specific thread, including generated replies.

## Testing

Run the comprehensive test suite using `pytest`:

```bash
pytest tests/
```

This runs unit and integration tests covering API endpoints, database operations, and guardrails.
