# Changelog

## [v1.1.0] - 2025-12-26

### Added

- **Webhook Endpoint**: New `/api/v1/email/webhook` endpoint for processing raw email content.
  - Features LLM-based intelligent parsing of sender, subject, and body.
  - Includes safety guardrails for raw content validation.
  - Supports various email formats (Gmail, Outlook, plain text, etc.).
- **Frontend Integration**: Updated "Submit Email" page to support pasting raw email content, which is processed via the new webhook.

### Changed

- **Deployment Structure**:
  - Consolidated frontend and backend Helm charts into a single `email-reply` chart.
  - Moved Dockerfiles to the project root:
    - `Dockerfile` -> `Dockerfile.backend`
    - `frontend/Dockerfile` -> `Dockerfile.frontend`
  - Updated `docker-compose.yml` to reflect the new Dockerfile locations.
- **Documentation**:
  - Updated `README.md` with recent changes and architecture details.
  - Updated `docs/How-to-Guide.md` with webhook usage instructions.

### Security

- Enhanced guardrails to validate content both before and after parsing in the webhook endpoint.
- Integrated safety rules into the LLM system prompt for better context-aware filtering.
