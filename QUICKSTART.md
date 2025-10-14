# Quick Start Guide

## Setup (Local Development)

1. **Install Python 3.9+**
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **Clone and Setup**
   ```bash
   git clone https://github.com/ddragosd/chatgpt-mcp-oauth.git
   cd chatgpt-mcp-oauth
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Adobe OAuth**
   - Visit [Adobe Developer Console](https://developer.adobe.com/console)
   - Create a new project or select existing
   - Add OAuth Web App credential
   - Copy Client ID and Client Secret
   
4. **Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials
   ```

5. **Run the Server**
   ```bash
   python server.py
   ```
   
   Server starts at: http://localhost:8000

## Setup (Docker)

1. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Adobe credentials
   ```

2. **Build and Run**
   ```bash
   docker-compose up -d
   ```

3. **Check Status**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### OAuth Metadata
```bash
curl http://localhost:8000/.well-known/oauth-authorization-server
```

### MCP Endpoint
The MCP endpoint is available at:
```
http://localhost:8000/mcp
```

## Connecting to ChatGPT

1. **Configure Custom GPT**
   - Go to ChatGPT Custom GPTs
   - Add MCP Server: `http://your-server:8000/mcp`
   - Configure OAuth with Adobe IMS endpoints

2. **Authorize**
   - ChatGPT will redirect to Adobe login
   - Sign in with your Adobe account
   - Grant permissions

3. **Use the Tool**
   - In ChatGPT, ask to use the `hello_user` tool
   - It will return: "Hello, [Your Name]! 👋"

## Troubleshooting

### Port Already in Use
```bash
# Change PORT in .env file
PORT=8080
```

### Dependencies Installation Failed
```bash
# Try upgrading pip first
pip install --upgrade pip
pip install -r requirements.txt
```

### OAuth Errors
- Verify Adobe credentials in .env
- Check Adobe Developer Console for correct URLs
- Ensure redirect URIs are configured

## Next Steps

- Deploy to a public server (AWS, GCP, Azure)
- Add HTTPS with reverse proxy (nginx, Caddy)
- Implement additional MCP tools
- Add logging and monitoring

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Adobe IMS API](https://developer.adobe.com/developer-console/docs/guides/authentication/)
- [FastMCP Docs](https://github.com/jlowin/fastmcp)
