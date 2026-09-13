"""FastAPI application used by local development and Fly deployment."""

from fastapi import FastAPI

app = FastAPI(title="Python Scaffold API")


@app.get("/health")  # [tag:health-route]
def health() -> dict[str, str]:
    """Report process health without requiring external services."""
    return {"status": "ok"}
