uv venv && source .venv/bin/activate
uv sync
cp .env.example .env
# edit RESOURCE_SERVER_URL (e.g., https://<ngrok>.app/mcp) and ADOBE_CLIENT_ID
uv run uvicorn server:app --host 0.0.0.0 --port 3000
