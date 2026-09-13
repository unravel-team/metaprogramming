FROM ghcr.io/astral-sh/uv:0.12.10 AS uv

FROM python:3.12-slim

WORKDIR /app
COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --locked --no-dev

EXPOSE 8080
CMD ["uv", "run", "--no-sync", "uvicorn", "python_scaffold.api:app", "--host", "0.0.0.0", "--port", "8080"]
