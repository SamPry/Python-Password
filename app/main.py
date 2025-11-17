"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI

from .routers import password

app = FastAPI(title="Password Service", version="1.0.0")
app.include_router(password.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
