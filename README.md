# chatgpt-mcp-oauth (chatgpt-version, uv)

A minimal **Model Context Protocol (MCP)** HTTP server you can connect to ChatGPT (Connectors → Create)
that verifies **Adobe OAuth** bearer tokens using the **userinfo** endpoint and exposes one tool:

- `hello` → replies with `Hello, <name>!` using the `name` claim from your Adobe token.

> This variant uses **uv** for dependency and environment management.

## Quick start (local) with `uv`

```bash
uv venv                     # creates .venv (if not present)
source .venv/bin/activate   # activate (Linux/macOS); on Windows: .venv\Scripts\activate
uv sync                     # install deps from pyproject.toml
cp .env.example .env
# edit .env to set RESOURCE_SERVER_URL and ADOBE_CLIENT_ID
uv run uvicorn server:app --host 0.0.0.0 --port 3000
```

Expose HTTPS (for ChatGPT):
```bash
ngrok http 3000
# set RESOURCE_SERVER_URL to https://<subdomain>.ngrok.app/mcp and restart
```

Create a connector in ChatGPT (Developer Mode → Connectors → Create):
- Name: Adobe Hello MCP
- URL: `https://<your-domain-or-ngrok>/mcp`
- Auth: OAuth (scopes: `openid` and `profile`)

Then in a chat where the connector is enabled, ask:
> Use Adobe Hello MCP → call the **hello** tool.

You should see: **Hello, Your Name! 👋**

## Adobe setup

- Create **OAuth Web App** credentials in Adobe Developer Console.
- Keep the Client ID handy; add the `profile` scope for UserInfo.
- The ChatGPT OAuth flow happens in the browser; you **do not** need a redirect handler on this server.
- This server only calls **UserInfo** to validate the token and extract the user name.

## Deploy

### Fly.io
```bash
fly launch --copy-config --no-deploy
fly secrets set RESOURCE_SERVER_URL=https://<your-app>.fly.dev/mcp ADOBE_OPENID_ISSUER=https://ims-na1.adobelogin.com ADOBE_CLIENT_ID=<client_id> REQUIRED_SCOPES="openid,profile"
fly deploy
```

### Cloud Run (Docker-based)
- Build/push the container and create a service (allow unauthenticated).
- Set env: `RESOURCE_SERVER_URL`, `ADOBE_OPENID_ISSUER`, `ADOBE_CLIENT_ID`, `REQUIRED_SCOPES`.

## Limitations

- This is a **minimal** MCP HTTP server aimed at ChatGPT connector testing.
- If the MCP SDK or ChatGPT’s connector protocol changes, update dependencies or the handler accordingly.
