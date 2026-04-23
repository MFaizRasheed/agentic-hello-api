# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI inference service wrapping an OpenAI Agents SDK agent backed by a local Ollama model. Persistent multi-turn conversations stored via SQLModel (SQLite default, Postgres supported).

## Commands

```bash
uv sync                              # Install dependencies
fastapi dev app/main.py              # Dev server (auto-reload, 127.0.0.1:8000)
fastapi run app/main.py              # Production server (0.0.0.0:8000)
```

Swagger UI: http://localhost:8000/docs

## Architecture

```
app/
├── main.py          # FastAPI app, lifespan, /conversations, /conversations/{cid}/chat
├── agent_setup.py   # Agent definition, tools (greet, calculate_sum, get_time), guardrails
├── db.py            # SQLModel Conversation/Message tables, SessionDep dependency
├── config.py        # pydantic-settings (Settings class)
├── schemas.py       # ChatIn/ChatOut/ConversationOut Pydantic schemas
└── tools.py         # Legacy tool utilities (unused by current agent)

shared/models/
├── ollama_provider.py   # get_model() → OpenAIChatCompletionsModel for Ollama
└── hf_provider.py       # Placeholder for HuggingFace provider
```

## Data Model

- `Conversation(id, title, created_at, messages[])` — one-to-many with Message
- `Message(id, conversation_id, role, content, created_at)`

DB file (`chats.db`) created in project root on first run.

## Key Patterns

- **Agent execution**: `run_agent(history, new_message)` — history is list of `{"role", "content"}` dicts loaded from DB
- **Streaming**: `stream_agent(...)` generator yields tokens via `Runner.run_streamed`
- **Guardrails**: Input (`validate_input`) and output (`validate_output`) validation in `agent_setup.py`
- **Lifespan**: `init_db()` called on startup — creates tables if not exist
- **Ollama model**: Must support tool-calling. Pull with `ollama pull <model>` (e.g., `minimax-m2.7:cloud`, `qwen2.5:7b`)

## Environment Variables

| Variable          | Default                       | Description                    |
|-------------------|-------------------------------|--------------------------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1`  | Ollama OpenAI-compatible endpoint |
| `OLLAMA_MODEL`    | `minimax-m2.7:cloud`          | Ollama model name              |
| `DATABASE_URL`    | `sqlite:///./chats.db`        | SQLAlchemy URL (Postgres also supported) |
