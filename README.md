# ChatGPT MCP Server with Adobe OAuth

An end-to-end MCP (Model Context Protocol) server implementation using Python, FastAPI, and the official FastMCP SDK. This server integrates with Adobe IMS OAuth to provide a personalized greeting tool that fetches your name from Adobe's UserInfo endpoint.

## Features

- ✅ **MCP Protocol**: Implements the official MCP specification using FastMCP
- ✅ **OAuth Integration**: Full Adobe IMS OAuth 2.0 support
- ✅ **Token Verification**: Validates access tokens against Adobe IMS
- ✅ **User Info**: Fetches user data from Adobe UserInfo API
- ✅ **Personalized Greeting**: Returns "Hello, [Your Name]!" using your Adobe profile
- ✅ **Streamable HTTP Transport**: Compatible with ChatGPT's Apps SDK

## Architecture

```
┌─────────────┐      OAuth Flow       ┌──────────────┐
│   ChatGPT   │ ◄──────────────────► │  Adobe IMS   │
└──────┬──────┘                       └──────────────┘
       │                                     ▲
       │ MCP Protocol                        │
       │ (Streamable HTTP)                   │ Token Verification
       │                                     │ UserInfo API
       ▼                                     │
┌─────────────────────────────────────────────┐
│     FastAPI + FastMCP Server                │
│  - OAuth Metadata Endpoint                  │
│  - MCP Tools (hello_user)                   │
│  - Token Verification                       │
└─────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.9 or higher
- Adobe Developer Account with OAuth credentials
- pip package manager

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ddragosd/chatgpt-mcp-oauth.git
cd chatgpt-mcp-oauth
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Adobe OAuth

1. Go to [Adobe Developer Console](https://developer.adobe.com/console)
2. Create a new project or select an existing one
3. Add "OAuth Server-to-Server" or "OAuth Web App" credential
4. Note your Client ID and Client Secret
5. Configure the redirect URIs as needed

### 5. Set Up Environment Variables

Copy the example environment file and fill in your Adobe credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Adobe credentials:

```env
ADOBE_CLIENT_ID=your_adobe_client_id_here
ADOBE_CLIENT_SECRET=your_adobe_client_secret_here
ADOBE_IMS_BASE_URL=https://ims-na1.adobelogin.com
ADOBE_IMS_USERINFO_URL=https://ims-na1.adobelogin.com/ims/userinfo/v2

HOST=0.0.0.0
PORT=8000
```

### 6. Run the Server

```bash
python server.py
```

Or using uvicorn directly:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

## Endpoints

### MCP Endpoint
- **URL**: `http://localhost:8000/mcp`
- **Protocol**: MCP over Streamable HTTP (SSE)
- **Description**: Main MCP protocol endpoint for ChatGPT integration

### OAuth Metadata
- **URL**: `http://localhost:8000/.well-known/oauth-authorization-server`
- **Description**: OAuth 2.0 Authorization Server Metadata (RFC 8414)

### Health Check
- **URL**: `http://localhost:8000/health`
- **Description**: Simple health check endpoint

## MCP Tools

### `hello_user`

Returns a personalized greeting using the user's name from Adobe.

**Parameters:**
- `access_token` (string): OAuth access token from Adobe IMS

**Returns:**
- A personalized greeting message: "Hello, [Your Name]! 👋"

**Example Response:**
```
Hello, John Doe! 👋
```

## Connecting to ChatGPT

1. Start the MCP server locally or deploy it to a public endpoint
2. In ChatGPT, navigate to Custom GPT or Apps configuration
3. Add the MCP server endpoint: `http://your-server:8000/mcp`
4. Configure OAuth settings pointing to Adobe IMS
5. Authorize the connection with your Adobe account
6. Use the `hello_user` tool to get a personalized greeting

## OAuth Flow

1. ChatGPT initiates OAuth flow with Adobe IMS
2. User authenticates with Adobe and grants permissions
3. ChatGPT receives an access token
4. When calling `hello_user`, the token is passed to the server
5. Server verifies the token with Adobe IMS
6. Server fetches user information from Adobe UserInfo endpoint
7. Server returns personalized greeting

## Development

### Project Structure

```
chatgpt-mcp-oauth/
├── server.py              # Main FastAPI + FastMCP server
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment configuration
├── .env                  # Your environment configuration (git-ignored)
├── .gitignore           # Git ignore patterns
└── README.md            # This file
```

### Key Dependencies

- **FastAPI**: Modern web framework for building APIs
- **FastMCP**: Official MCP Python SDK
- **uvicorn**: ASGI server for FastAPI
- **httpx**: Async HTTP client for Adobe IMS calls
- **pydantic**: Data validation and settings management
- **python-dotenv**: Environment variable management

## Testing

### Manual Testing

1. Start the server
2. Check health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

3. Check OAuth metadata:
   ```bash
   curl http://localhost:8000/.well-known/oauth-authorization-server
   ```

4. Test the MCP endpoint (requires proper MCP client)

### With Adobe Token

If you have a valid Adobe access token, you can test the tool directly:

```python
import httpx
import asyncio

async def test_hello():
    token = "your_adobe_access_token"
    # Use MCP client to call the hello_user tool with the token
    pass

asyncio.run(test_hello())
```

## Troubleshooting

### Common Issues

**"Invalid or expired access token"**
- Ensure your Adobe access token is valid
- Check that your Adobe OAuth credentials are correct in `.env`
- Verify that the token has not expired

**"Failed to fetch user info"**
- Check your Adobe IMS URLs are correct
- Verify network connectivity to Adobe IMS
- Ensure your Adobe account has proper permissions

**Server won't start**
- Check that port 8000 is not already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version is 3.9 or higher

## Security Considerations

- **Never commit `.env` file**: Keep your credentials secure
- **Use HTTPS in production**: Deploy with proper TLS certificates
- **Token validation**: Server validates all tokens with Adobe IMS
- **Environment variables**: All sensitive config via environment variables

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Adobe IMS Documentation](https://developer.adobe.com/developer-console/docs/guides/authentication/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
