# Adobe Hello MCP Server Implementation

## Overview

This is a Model Context Protocol (MCP) server that integrates with Adobe Identity Management Services (IMS) for OAuth 2.0 authentication. The server provides a simple "hello" tool that greets users with their Adobe identity information.

## Architecture

### Authentication Flow
- **Stateless Bearer Token Validation**: No token persistence required
- **Adobe IMS Integration**: Uses Adobe's OAuth 2.0 endpoints for authentication
- **Per-Request Validation**: Each request validates the Bearer token via Adobe's userinfo endpoint

### Protocol Support
- **JSON-RPC 2.0**: Standard MCP protocol implementation
- **MCP Protocol Version**: 2025-03-26
- **OAuth 2.0**: RFC 6749 compliant with Adobe IMS

## Key Components

### 1. OAuth Configuration

#### Environment Variables
```bash
ADOBE_OPENID_ISSUER=https://ims-na1.adobelogin.com
ADOBE_USERINFO=https://ims-na1.adobelogin.com/ims/userinfo/v2
ADOBE_CLIENT_ID=your_adobe_client_id
ADOBE_CLIENT_SECRET=your_adobe_client_secret
RESOURCE_SERVER_URL=https://your-domain.ngrok-free.dev/mcp
REQUIRED_SCOPES=AdobeID,openid,read_organizations,additional_info.projectedProductContext,additional_info.job_function
```

#### Adobe OAuth Endpoints
- **Authorization**: `https://ims-na1.adobelogin.com/ims/authorize/v2`
- **Token**: `https://ims-na1.adobelogin.com/ims/token/v3`
- **UserInfo**: `https://ims-na1.adobelogin.com/ims/userinfo/v2`
- **JWKS**: `https://ims-na1.adobelogin.com/ims/keys`

### 2. Discovery Endpoints

#### OAuth 2.0 Authorization Server Metadata (`/.well-known/oauth-authorization-server`)
- **Standard**: RFC 8414 compliant
- **Purpose**: Tells ChatGPT where Adobe OAuth endpoints are located
- **Key Feature**: Includes `registration_endpoint` pointing to our proxy endpoint

#### OpenID Connect Discovery (`/.well-known/openid-configuration`)
- **Standard**: OpenID Connect Discovery 1.0
- **Purpose**: Provides OpenID Connect metadata for ChatGPT
- **Scope**: Adobe-specific scopes supported

#### MCP Server Configuration (`/.well-known/mcp-server`)
- **Purpose**: MCP-specific server metadata
- **Contains**: Tool definitions, OAuth configuration, server info

### 3. Dynamic Client Registration Proxy

#### Endpoint: `POST /register`
- **Problem Solved**: Adobe IMS doesn't support RFC 7591 Dynamic Client Registration
- **Solution**: Returns pre-configured Adobe client credentials as if they were dynamically registered
- **Response Format**: Standard RFC 7591 client registration response
- **Status**: 201 Created (simulates successful registration)

**Implementation Strategy:**
```python
# ChatGPT sends dynamic registration request
# Server responds with existing Adobe credentials
return {
    "client_id": ADOBE_CLIENT_ID,
    "client_secret": ADOBE_CLIENT_SECRET,
    "grant_types": ["authorization_code", "refresh_token"],
    "scope": " ".join(REQUIRED_SCOPES)
}
```

### 4. MCP Protocol Implementation

#### Main Endpoint: `POST /`
- **Protocol**: JSON-RPC 2.0
- **Authentication**: Bearer token validation on every request
- **Supported Methods**:
  - `initialize` - Server initialization and capability negotiation
  - `tools/list` - Lists available tools
  - `tools/call` - Executes tool with user context

#### Authentication Middleware
```python
async def authenticate_request(token: str) -> str:
    """Validates Adobe Bearer token and returns user name"""
    # Calls Adobe userinfo endpoint with Bearer token
    # Returns user's name/preferred_username
    # No token storage - validates per request
```

#### Tool Definition
```json
{
    "name": "hello",
    "description": "Return a greeting using your Adobe OAuth identity",
    "inputSchema": {
        "type": "object",
        "properties": {}
    }
}
```

## Request Flow

### 1. ChatGPT Registration Process
1. **Discovery**: ChatGPT fetches `/.well-known/oauth-authorization-server`
2. **Dynamic Registration**: ChatGPT POSTs to `/register`
3. **Response**: Server returns pre-configured Adobe credentials
4. **OAuth Flow**: ChatGPT initiates OAuth with Adobe using returned credentials

### 2. Tool Usage Flow
1. **Authentication**: User completes Adobe OAuth in ChatGPT
2. **MCP Initialize**: ChatGPT sends `initialize` request with Bearer token
3. **Tool Discovery**: ChatGPT sends `tools/list` request
4. **Tool Execution**: User triggers tool, ChatGPT sends `tools/call` request
5. **Response**: Server validates token, gets Adobe user info, returns personalized greeting

## Security Features

### Stateless Design
- **No Session Storage**: Server doesn't store user tokens or sessions
- **Per-Request Validation**: Every request validates Bearer token with Adobe
- **No Persistent State**: Server can be restarted without losing user sessions

### OAuth Security
- **Bearer Token Validation**: Standard OAuth 2.0 Bearer token usage (RFC 6750)
- **Adobe Token Validation**: Uses Adobe's userinfo endpoint for token validation
- **Scope Validation**: Enforces required Adobe scopes
- **Error Handling**: Proper OAuth error responses

### Adobe Integration Security
- **Pre-registered Client**: Uses manually registered Adobe OAuth application
- **Client Credentials**: Stored in environment variables (not hardcoded)
- **Secure Endpoints**: All OAuth endpoints use HTTPS
- **Adobe IMS**: Leverages Adobe's enterprise-grade identity management

## Technical Benefits

### For Developers
- **Simple Architecture**: No complex token management or database requirements
- **Standard Protocols**: Uses well-established OAuth 2.0 and JSON-RPC 2.0 standards
- **Debuggable**: Clear separation of concerns and comprehensive logging
- **Maintainable**: Minimal dependencies and straightforward code structure

### For Operations
- **Scalable**: Stateless design allows horizontal scaling
- **Reliable**: No database dependencies or persistent state to manage
- **Secure**: Leverages Adobe's battle-tested identity infrastructure
- **Monitorable**: Standard HTTP endpoints with clear error responses

## Deployment

### Requirements
- **Python 3.8+** with FastAPI, httpx, python-dotenv
- **Adobe Developer Console** account with OAuth Web application
- **HTTPS Endpoint** (required for OAuth, provided via ngrok in development)
- **Environment Variables** configured with Adobe OAuth credentials

### Docker Support
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration
```bash
# Adobe OAuth Configuration (Required)
ADOBE_CLIENT_ID=your_adobe_client_id
ADOBE_CLIENT_SECRET=your_adobe_client_secret

# Server Configuration
RESOURCE_SERVER_URL=https://your-domain.com/mcp
REQUIRED_SCOPES=AdobeID,openid,read_organizations

# Optional Adobe Configuration
ADOBE_OPENID_ISSUER=https://ims-na1.adobelogin.com
ADOBE_USERINFO=https://ims-na1.adobelogin.com/ims/userinfo/v2
```

## Troubleshooting

### Common Issues

#### "Dynamic Client Registration Not Supported"
- **Cause**: ChatGPT attempting RFC 7591 with Adobe (not supported)
- **Solution**: Our `/register` endpoint handles this by returning pre-configured credentials

#### "OAuth Configuration Error"
- **Cause**: Missing or incorrect Adobe client credentials
- **Check**: `/oauth/validate` endpoint shows current configuration status

#### "Token Validation Failed"
- **Cause**: Invalid/expired Bearer token or Adobe API issues
- **Debug**: Check Adobe userinfo endpoint response and token format

### Debug Endpoints
- **GET /oauth/validate**: Shows current OAuth configuration status
- **GET /oauth-setup-guide**: Detailed setup instructions for ChatGPT integration
- **GET /healthz**: Basic health check

## Standards Compliance

### RFC Standards
- **RFC 6749**: OAuth 2.0 Authorization Framework
- **RFC 6750**: OAuth 2.0 Bearer Token Usage
- **RFC 8414**: OAuth 2.0 Authorization Server Metadata
- **RFC 7591**: OAuth 2.0 Dynamic Client Registration (proxied)

### MCP Standards
- **MCP Protocol**: 2025-03-26 specification
- **JSON-RPC 2.0**: Standard request/response format
- **Tool Schema**: Standard MCP tool definition format

## Future Enhancements

### Performance Optimizations
- **JWT Token Validation**: Validate Adobe JWT tokens locally using JWKS (if Adobe issues JWTs)
- **Short-lived Caching**: 5-minute in-memory cache for userinfo responses
- **Connection Pooling**: Reuse HTTP connections to Adobe endpoints

### Additional Tools
- **Adobe API Integration**: Tools that call Adobe Creative Cloud APIs
- **User Profile Tools**: Access Adobe user profile information
- **Organization Tools**: List Adobe organizations and projects

### Enhanced Security
- **Scope Validation**: Validate token scopes against tool requirements
- **Rate Limiting**: Implement request rate limiting per user
- **Audit Logging**: Log all tool usage for security monitoring