# Quick Installation Guide

This guide will help you get the Context Aware AI Email Reply API up and running in minutes.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (or compatible LLM endpoint)

## Installation Steps

### 1. Clone the Repository

```bash
git clone git@github.com:mrankitvish/context-aware-ai-email-reply.git
cd context-aware-ai-email-reply
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1
DATABASE_URL=postgresql://user:password@localhost:5432/emaildb
EOF
```

### 3. Start with Docker Compose

```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`.

### 4. Verify Installation

```bash
curl http://localhost:8000
```

You should see: `{"message":"Welcome to Context Aware AI Email Reply API"}`

### 5. Access API Documentation

Open your browser and navigate to:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Quick Test

Submit a test email:

```bash
curl -X POST http://localhost:8000/api/v1/email/submit \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Product Inquiry",
    "body": "Hi, I would like to know more about your enterprise plan.",
    "sender": "customer@example.com"
  }'
```

## Next Steps

- See [How-to-Guide.md](./How-to-Guide.md) for detailed usage instructions
- See [Advanced-Configuration-Guide.md](./Advanced-Configuration-Guide.md) for customization options
