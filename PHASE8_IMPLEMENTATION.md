# AgentOps-OS Phase 8

Phase 8 adds a user-configurable generation-provider fallback chain and a persistent human-approval gate for side-effecting tools.

## AI providers

The `/api/v1/ai-providers` API stores per-user provider configuration. Supported providers:

- `openai`: OpenAI-compatible Chat Completions structured output.
- `groq`: Groq-hosted models using its OpenAI-compatible endpoint. Select a Llama model in `model_name`. The adapter uses JSON-object mode and validates the returned payload locally because Groq strict JSON-schema support is model-dependent.
- `ollama`: local Ollama structured generation. The default is the existing Qwen model.

Lower `priority` values are attempted first. Only provider request/configuration failures are eligible for fallback. Model refusals stop the chain and are not bypassed by trying another provider. Prompt validation errors are also not retried against another provider.

If a user has not saved provider rows, AgentOps-OS uses `OPENAI_API_KEY` (when configured) first and the configured local Ollama model second. Once the user saves provider rows, only enabled saved rows are used, in priority order.

### Encrypting API keys

Hosted provider credentials are encrypted with Fernet before they are written to PostgreSQL. Generate one deployment key:

```powershell
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Set the resulting value in the repository-root `.env`:

```dotenv
AI_CREDENTIAL_ENCRYPTION_KEY=<generated-fernet-key>
```

Do not commit `.env`, the generated key, or provider API keys. Back up the encryption key securely. If it is lost or rotated without re-encrypting existing rows, stored API keys cannot be decrypted.

### Configure providers

Use an authenticated `PUT /api/v1/ai-providers/{provider_name}` request. Example:

```json
{
  "model_name": "gpt-5.5",
  "api_key": "<OpenAI API key>",
  "priority": 0,
  "enabled": true
}
```

Configure Groq with `provider_name=groq`, a supported Llama model name, and a Groq API key. Configure local Ollama with `provider_name=ollama`, a local model such as `qwen3.5:0.8b`, and optionally a local base URL. The API never returns the plaintext key; responses expose only `api_key_configured`.

`POST /api/v1/ai-providers/test` runs a small structured-output health check through the configured fallback chain.

Embedding configuration remains independent. Phase 7 continues using `embeddinggemma` and the existing 768-dimensional pgvector column.

## Human approvals

A tool must be marked by trusted application code with `requires_approval=True` in its `ToolDefinition`. The value is not accepted from task input or an LLM-generated plan. When execution reaches that tool:

1. The workflow pauses and moves to `awaiting_approval`.
2. The task moves to `awaiting_approval`.
3. An `approval_requests` row is created with a redacted input snapshot and expiry.
4. An execution event and append-only audit log entry are written.
5. A different administrator can approve or reject the request.
6. Approval resumes the workflow; successful execution marks the request `executed`.
7. Rejection, cancellation or expiry cancels the workflow.

Only an administrator can approve or reject. The requester cannot approve their own request. The requester or an administrator can cancel a pending request. Pending request details are owner-scoped; administrators can inspect the inbox.

The current built-in tools are read-only text utilities, so none is marked as requiring approval. Register application-specific tools with `create_app(settings, tool_registrars=[...])`. Each registrar receives a `ToolRegistry` and must register trusted `ToolDefinition` objects. The same registered tool set is used by planning, execution, knowledge agents, and approval resumption. Side-effecting tools must set `requires_approval=True` in their trusted definition. The Phase 8 approval integration test registers such a protected tool to verify pause, approval, resume and execution.

## Migration and dependencies

Phase 8 adds Alembic revision `0003`, after Phase 7 revision `0002`. It creates:

- `ai_provider_configs`
- `approval_requests`

After applying the individual files, run from `backend/`:

```powershell
uv sync --extra dev
uv run alembic upgrade head
```

The migration safety checks remain enabled. The target should be your development database for a local development upgrade, and the integration fixtures use only guarded test/disposable database names.
