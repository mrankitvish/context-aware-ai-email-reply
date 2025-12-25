# Advanced Configuration Guide

This guide covers advanced configuration options for the Context Aware AI Email Reply system, including environment variables, LLM providers, and Helm chart customization.

## Environment Variables

The application is configured via environment variables, which can be set in a `.env` file or passed to the container.

| Variable          | Description                  | Default                     | Required |
| ----------------- | ---------------------------- | --------------------------- | -------- |
| `OPENAI_API_KEY`  | API Key for the LLM provider | -                           | Yes      |
| `OPENAI_MODEL`    | Model name to use            | `gpt-4o`                    | No       |
| `OPENAI_BASE_URL` | Base URL for the LLM API     | `https://api.openai.com/v1` | No       |
| `DATABASE_URL`    | SQLAlchemy connection string | `postgresql://...`          | Yes      |

## LLM Configuration

### Using OpenAI

Standard configuration for OpenAI:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
```

### Using Azure OpenAI

To use Azure OpenAI, you may need to adjust the `OPENAI_BASE_URL` and `OPENAI_API_KEY` accordingly. Note that the current implementation uses `langchain-openai` which supports standard OpenAI-compatible endpoints.

### Using Local LLMs (e.g., Ollama, vLLM)

You can point the application to a local LLM server that provides an OpenAI-compatible API.

Example for Ollama:

```env
OPENAI_API_KEY=unused
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3
```

## Helm Chart Configuration

The Helm chart is located in `helm/email-reply-api`. You can customize the deployment by modifying `values.yaml`.

### Key Values

| Key                   | Description                              | Default           |
| --------------------- | ---------------------------------------- | ----------------- |
| `replicaCount`        | Number of pod replicas                   | `1`               |
| `image.repository`    | Docker image repository                  | `email-reply-api` |
| `image.tag`           | Docker image tag                         | `latest`          |
| `service.type`        | Kubernetes Service type                  | `ClusterIP`       |
| `persistence.enabled` | Enable persistent storage for PostgreSQL | `true`            |
| `persistence.size`    | Size of the persistent volume            | `1Gi`             |
| `env.OPENAI_API_KEY`  | API Key (can also use secrets)           | `""`              |

### Production Deployment Tips

1.  **Secrets Management**: Do not commit `OPENAI_API_KEY` in `values.yaml`. Use Kubernetes Secrets or an external secrets manager.

### Database Configuration

The `docker-compose.yml` is pre-configured to use a PostgreSQL container.

- **Local Development**: Uses PostgreSQL via Docker Compose.
- **Production**: Point `DATABASE_URL` to your managed PostgreSQL instance (e.g., RDS, Cloud SQL).

```env
DATABASE_URL=postgresql://user:password@localhost:5432/emaildb
```

3.  **Ingress**: Enable Ingress in `values.yaml` to expose the API externally with TLS.
