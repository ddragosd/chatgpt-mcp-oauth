from math import log
import os
import json
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv

load_dotenv()

ADOBE_OPENID_ISSUER = os.getenv("ADOBE_OPENID_ISSUER", "https://ims-na1.adobelogin.com")
ADOBE_USERINFO = os.getenv("ADOBE_USERINFO", f"{ADOBE_OPENID_ISSUER}/ims/profile/v1")
ADOBE_CLIENT_ID = os.getenv("ADOBE_CLIENT_ID", "")
ADOBE_CLIENT_SECRET = os.getenv("ADOBE_CLIENT_SECRET", "")
RESOURCE_SERVER_URL = os.getenv("RESOURCE_SERVER_URL", "https://unscaled-kenny-unicellular.ngrok-free.dev/mcp")
REQUIRED_SCOPES = [s.strip() for s in os.getenv("REQUIRED_SCOPES", "openid,profile").split(",") if s.strip()]

app = FastAPI(title="Adobe Hello MCP (minimal, uv)")

def mcp_error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})

async def get_name_from_adobe(access_token: str) -> Optional[str]:
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {}
    if ADOBE_CLIENT_ID:
        params["client_id"] = ADOBE_CLIENT_ID
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(ADOBE_USERINFO, headers=headers, params=params)
    if r.status_code != 200:
        print(f"Adobe profile request failed: {r.status_code} - {r.text}")
        return None
    info = r.json()
    # print(f"Adobe profile response: {info}")

    # Adobe profile endpoint returns different field names than userinfo
    return (info.get("displayName") or
            info.get("name") or
            info.get("first_name") or
            info.get("firstName") or
            info.get("email") or
            info.get("sub", "Adobe User"))

@app.post("/mcp")
async def mcp_endpoint(request: Request) -> Response:
    """
    Minimal Streamable HTTP-style handler:
    - Expects a Bearer token (Adobe) in Authorization header.
    - Accepts a small JSON body { "tool": "hello", "params": {} }.
    - Responds with a JSON result or 401 to trigger OAuth in ChatGPT.
    """
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        return mcp_error(401, "unauthorized", "Sign in with Adobe to use this server.")

    token = auth.split(" ", 1)[1].strip()
    name = await get_name_from_adobe(token)
    if not name:
        return mcp_error(401, "unauthorized", "Invalid or expired Adobe token. Please sign in again.")

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    tool = payload.get("tool", "hello")
    if tool != "hello":
        return mcp_error(400, "unknown_tool", f"Unknown tool '{tool}'. Try 'hello'.")

    result: Dict[str, Any] = {
        "content": [{"type": "text", "text": f"Hello, {name}! 👋"}],
        "structuredContent": {"name": name},
        "tool": "hello"
    }
    return JSONResponse(result)

@app.get("/")
async def root():
    """Root endpoint - basic server info"""
    return {
        "name": "Adobe Hello MCP Server",
        "description": "MCP server with Adobe OAuth authentication",
        "version": "0.1.0"
    }

@app.post("/")
async def mcp_root_endpoint(request: Request) -> Response:
    """
    MCP JSON-RPC 2.0 endpoint at root path (ChatGPT expects MCP at /).
    Handles initialize, tools/list, tools/call, etc.
    """
    print("=" * 60)
    print("MCP Request Debug:")
    print("=" * 60)

    # Log all headers for debugging
    print("HEADERS:")
    for name, value in request.headers.items():
        if name.lower() == "authorization":
            # Mask token for security but show if it exists
            print(f"  {name}: {'Bearer ***' + value[-10:] if value.startswith('Bearer ') else repr(value)}")
        else:
            print(f"  {name}: {value}")

    auth = request.headers.get("authorization", "")
    print(f"\nAuth header: {repr(auth[:50])}{'...' if len(auth) > 50 else ''}")

    if not auth.lower().startswith("bearer "):
        print("❌ NO BEARER TOKEN FOUND")
        return mcp_error(401, "unauthorized", "Sign in with Adobe to use this server.")

    token = auth.split(" ", 1)[1].strip()
    print(f"Token extracted: {token[:20]}...{token[-10:] if len(token) > 30 else token}")

    print("🔍 Validating token with Adobe...")
    name = await get_name_from_adobe(token)
    if not name:
        print("❌ ADOBE TOKEN VALIDATION FAILED")
        return mcp_error(401, "unauthorized", "Invalid or expired Adobe token. Please sign in again.")

    print(f"✅ Token valid for user: {name}")
    print("=" * 60)

    try:
        payload = await request.json()
    except Exception:
        return mcp_error(400, "invalid_request", "Invalid JSON-RPC request")

    # Handle JSON-RPC 2.0 MCP protocol
    method = payload.get("method")
    request_id = payload.get("id")
    params = payload.get("params", {})

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "adobe-hello-mcp",
                    "version": "0.1.0"
                }
            }
        })

    elif method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "hello",
                        "description": "Return a greeting using your Adobe OAuth identity",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        })

    elif method == "tools/call":
        tool_name = params.get("name", "hello")
        if tool_name != "hello":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool '{tool_name}'. Try 'hello'."
                }
            })

        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Hello, {name}! 👋"
                    }
                ]
            }
        })

    else:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method '{method}' not found"
            }
        })

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/oauth/validate")
async def oauth_validate():
    """
    Endpoint to validate OAuth configuration.
    Returns the current OAuth setup status.
    """
    return {
        "oauth_configured": bool(ADOBE_CLIENT_ID and ADOBE_CLIENT_SECRET),
        "issuer": ADOBE_OPENID_ISSUER,
        "client_id": ADOBE_CLIENT_ID[:8] + "..." if ADOBE_CLIENT_ID else None,
        "scopes": REQUIRED_SCOPES,
        "endpoints": {
            "authorization": f"{ADOBE_OPENID_ISSUER}/ims/authorize/v2",
            "token": f"{ADOBE_OPENID_ISSUER}/ims/token/v3",
            "userinfo": ADOBE_USERINFO
        }
    }

@app.get("/.well-known/oauth-authorization-server")
async def oauth_authorization_server():
    """
    RFC 8414 OAuth 2.0 Authorization Server Metadata.
    Standard format that indicates no dynamic registration.
    """
    return {
        "issuer": ADOBE_OPENID_ISSUER,
        "authorization_endpoint": f"{ADOBE_OPENID_ISSUER}/ims/authorize/v2",
        "token_endpoint": f"{ADOBE_OPENID_ISSUER}/ims/token/v3",
        "userinfo_endpoint": f"{ADOBE_OPENID_ISSUER}/ims/profile/v1",
        "jwks_uri": f"{ADOBE_OPENID_ISSUER}/ims/keys",
        "scopes_supported": REQUIRED_SCOPES,
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
        "service_documentation": f"{RESOURCE_SERVER_URL.rstrip('/mcp')}/oauth-setup-guide",
        "subject_types_supported": ["public"],
        "registration_endpoint": f"{RESOURCE_SERVER_URL.rstrip('/mcp')}/register"
    }

@app.post("/register")
async def client_registration(request: Request):
    """
    Dynamic client registration endpoint.
    Returns the pre-configured Adobe client credentials since Adobe IMS
    doesn't support dynamic registration - we return our manually registered client.
    """
    try:
        registration_request = await request.json()
    except:
        registration_request = {}

    if not ADOBE_CLIENT_ID:
        return JSONResponse(
            status_code=400,
            content={
                "error": "server_error",
                "error_description": "Server not configured with Adobe client credentials"
            }
        )

    # Return the pre-configured Adobe client credentials
    # This simulates dynamic registration by returning our existing client
    return JSONResponse(
        status_code=201,
        content={
            "client_id": ADOBE_CLIENT_ID,
            "client_secret": ADOBE_CLIENT_SECRET,
            # "client_id_issued_at": 1640995200,  # Static timestamp
            "client_name": registration_request.get("client_name", "ChatGPT MCP Client"),
            "redirect_uris": registration_request.get("redirect_uris", []),
            "grant_types": ["authorization_code", "refresh_token"],
            # "response_types": ["code"],
            "scope": " ".join(REQUIRED_SCOPES),
            # "token_endpoint_auth_method": "client_secret_post"
        }
    )

@app.get("/.well-known/mcp-server")
async def mcp_server_config():
    """
    MCP Server configuration with OAuth details.
    """
    return {
        "name": "adobe-hello-mcp",
        "version": "0.1.0",
        "transport": "http",
        "endpoint": RESOURCE_SERVER_URL,
        "auth": {
            "type": "oauth2",
            "issuer": ADOBE_OPENID_ISSUER,
            "authorization_endpoint": f"{ADOBE_OPENID_ISSUER}/ims/authorize/v2",
            "token_endpoint": f"{ADOBE_OPENID_ISSUER}/ims/token/v3",
            "scopes": REQUIRED_SCOPES
        },
        "tools": [
            {
                "name": "hello",
                "title": "Hello with Adobe Name",
                "description": "Return a greeting using your Adobe OAuth identity",
                "input_schema": {"type": "object", "properties": {}},
                "security": {"type": "oauth2", "scopes": REQUIRED_SCOPES}
            }
        ]
    }

# Using oauth-authorization-server endpoint above for MCP configuration

@app.get("/.well-known/openid-configuration")
async def openid_configuration():
    """
    OpenID Connect Discovery metadata.
    Explicitly omits registration_endpoint to indicate no dynamic registration.
    """
    return {
        "issuer": ADOBE_OPENID_ISSUER,
        "authorization_endpoint": f"{ADOBE_OPENID_ISSUER}/ims/authorize/v2",
        "token_endpoint": f"{ADOBE_OPENID_ISSUER}/ims/token/v3",
        "userinfo_endpoint": f"{ADOBE_OPENID_ISSUER}/ims/profile/v1",
        "jwks_uri": f"{ADOBE_OPENID_ISSUER}/ims/keys",
        "scopes_supported": REQUIRED_SCOPES,
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "subject_types_supported": ["public"],
        "claims_supported": ["sub", "name", "preferred_username", "given_name", "family_name", "email"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
        "service_documentation": f"{RESOURCE_SERVER_URL.rstrip('/mcp')}/oauth-setup-guide"
    }

@app.get("/oauth-setup-guide")
async def oauth_setup_guide():
    """
    Service documentation explaining OAuth setup for ChatGPT.
    """
    return {
        "title": "Adobe Hello MCP OAuth Setup",
        "description": "This MCP server uses Adobe IMS for authentication with pre-configured OAuth credentials.",
        "oauth_provider": "Adobe Identity Management Services (IMS)",
        "client_registration": {
            "method": "manual",
            "required": True,
            "description": "OAuth client must be pre-registered with Adobe Developer Console"
        },
        "setup_instructions": {
            "step_1": "The MCP server has been pre-configured with Adobe OAuth credentials",
            "step_2": "Client ID and Secret are already configured in the server environment",
            "step_3": "ChatGPT should use the standard OAuth authorization flow with these pre-configured credentials",
            "step_4": "No dynamic client registration is needed or supported"
        },
        "oauth_config": {
            "client_id": ADOBE_CLIENT_ID if ADOBE_CLIENT_ID else "CONFIGURED_IN_ENV",
            "issuer": ADOBE_OPENID_ISSUER,
            "authorization_endpoint": f"{ADOBE_OPENID_ISSUER}/ims/authorize/v2",
            "token_endpoint": f"{ADOBE_OPENID_ISSUER}/ims/token/v3",
            "scopes": REQUIRED_SCOPES
        },
        "notes": [
            "This server validates Bearer tokens by calling Adobe's profile endpoint",
            "No token storage or session persistence is used",
            "Each request is validated independently"
        ]
    }

