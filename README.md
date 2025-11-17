# Python-Password

Password validation, generation, and strength scoring service powered by FastAPI.

## Features

- **Validation** – length and character-class checks backed by centralized policy rules.
- **Generation** – cryptographically secure passwords that always satisfy the policy baseline.
- **Strength scoring** – entropy-informed score (0–10) with weak/medium/strong labels.
- **REST API** – async FastAPI endpoints for `/password/validate`, `/password/generate`, `/password/strength`, and `/password/full` plus `/health`.

## Requirements

- Python 3.12+
- `pip` for dependency management

Install the runtime dependencies with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the API server

Start the FastAPI app with Uvicorn:

```bash
uvicorn app.main:app --reload
```

By default the server listens on `http://127.0.0.1:8000`. Use the built-in docs at `http://127.0.0.1:8000/docs` to explore and exercise the endpoints interactively.

## Example requests

```bash
# Validate an existing password
curl -X POST http://127.0.0.1:8000/password/validate \
  -H "Content-Type: application/json" \
  -d '{"password": "Sup3r$ecret"}'

# Generate a 20-character password
curl -X POST http://127.0.0.1:8000/password/generate \
  -H "Content-Type: application/json" \
  -d '{"length": 20}'

# Full analysis with automatic password generation
curl -X POST http://127.0.0.1:8000/password/full \
  -H "Content-Type: application/json" \
  -d '{"length": 18}'
```

## Health check

`GET /health` returns `{ "status": "ok" }` for readiness/liveness probing.

## Testing

Compile the application modules to ensure there are no syntax errors:

```bash
python -m compileall app
```

## Next steps

- Add persistence for logging/auditing flows (SQLModel or SQLite).
- Expose CLI helpers for quick local validation or generation.
- Layer on authentication/rate limiting for production deployments.
