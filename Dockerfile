FROM python:3.11-slim
WORKDIR /app

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

COPY pyproject.toml /app/
RUN uv sync --frozen

COPY . /app
ENV PORT=3000
CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3000"]
