# ChatGPT Integration Guide

This guide explains how to connect this MCP server to ChatGPT and use the `hello_user` tool.

## Prerequisites

- MCP server running (locally or on a public endpoint)
- Adobe OAuth credentials configured
- ChatGPT Plus or Enterprise account

## Step 1: Start the MCP Server

### Option A: Local Development
```bash
# Configure environment
cp .env.example .env
# Edit .env with your Adobe credentials

# Install and run
pip install -r requirements.txt
python server.py
```

Server will be available at `http://localhost:8000`

### Option B: Docker Deployment
```bash
# Configure environment
cp .env.example .env
# Edit .env with your Adobe credentials

# Run with Docker
docker-compose up -d
```

### Option C: Public Deployment
Deploy to a cloud provider (AWS, GCP, Azure, Heroku, etc.) with:
- Python 3.9+ runtime
- Environment variables configured
- Public HTTPS endpoint

**Important**: For ChatGPT integration, you'll need a publicly accessible endpoint with HTTPS.

## Step 2: Verify Server is Running

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"Adobe OAuth MCP Server"}

# OAuth metadata
curl http://localhost:8000/.well-known/oauth-authorization-server

# Should return OAuth configuration
```

## Step 3: Configure ChatGPT

### For Custom GPTs

1. **Go to ChatGPT**
   - Navigate to https://chat.openai.com
   - Click on your profile
   - Select "My GPTs" or "Create a GPT"

2. **Create or Edit a Custom GPT**
   - Click "Create a GPT" or edit an existing one
   - Go to the "Configure" tab

3. **Add MCP Server**
   - In the configuration, look for "Actions" or "Tools"
   - Add a new action/tool
   - Set the endpoint to your MCP server:
     - If local (for testing): `http://localhost:8000/mcp`
     - If deployed: `https://your-domain.com/mcp`

4. **Configure OAuth**
   - Authentication Type: OAuth 2.0
   - Authorization URL: `https://ims-na1.adobelogin.com/ims/authorize/v2`
   - Token URL: `https://ims-na1.adobelogin.com/ims/token/v3`
   - Client ID: Your Adobe Client ID
   - Client Secret: Your Adobe Client Secret
   - Scopes: `openid profile email`

### For ChatGPT Apps (Future)

When ChatGPT Apps supports MCP:

```json
{
  "mcp_servers": [
    {
      "name": "Adobe OAuth MCP",
      "endpoint": "https://your-domain.com/mcp",
      "transport": "sse",
      "oauth": {
        "discovery_url": "https://your-domain.com/.well-known/oauth-authorization-server"
      }
    }
  ]
}
```

## Step 4: Authorize with Adobe

1. **First Use**
   - When you first try to use the tool, ChatGPT will prompt for authorization
   - Click "Authorize" or "Connect"

2. **Adobe Login**
   - You'll be redirected to Adobe IMS login page
   - Sign in with your Adobe account
   - If you don't have one, create a free Adobe account at adobe.com

3. **Grant Permissions**
   - Adobe will show what permissions the app is requesting:
     - Read your profile information
     - Read your email address
   - Click "Allow" or "Authorize"

4. **Return to ChatGPT**
   - You'll be redirected back to ChatGPT
   - The authorization is now complete

## Step 5: Use the Tool

Once authorized, you can use the `hello_user` tool in your conversation:

### Example Conversations

**User**: "Use the hello_user tool to greet me"

**ChatGPT**: Let me use the Adobe OAuth MCP tool to get your personalized greeting.
[Calls hello_user tool with access token]
The greeting from the MCP server is: "Hello, John Doe! 👋"

---

**User**: "What's my name according to Adobe?"

**ChatGPT**: Let me check using the hello_user tool.
[Calls hello_user tool]
According to your Adobe profile, your name is John Doe!

---

**User**: "Can you greet me using my Adobe profile?"

**ChatGPT**: Of course! 
[Calls hello_user tool]
Hello, John Doe! 👋

## Troubleshooting

### "Server not reachable"
- Check that the server is running: `curl http://localhost:8000/health`
- Verify the URL is correct
- Ensure firewall allows traffic
- For production, make sure you're using HTTPS

### "OAuth authorization failed"
- Verify Adobe credentials in `.env` are correct
- Check that redirect URIs are properly configured in Adobe Developer Console
- Make sure the authorization and token URLs are correct

### "Invalid or expired access token"
- The access token may have expired
- Try disconnecting and reconnecting the OAuth integration
- Check that the token is being passed correctly to the tool

### "Name not found"
- Verify your Adobe profile has a name set
- Check the UserInfo endpoint URL is correct
- The tool falls back to email if name is not available

## Advanced Configuration

### Custom Adobe IMS Endpoints

If you're using a different Adobe IMS region:

```env
ADOBE_IMS_BASE_URL=https://ims-na1-stg1.adobelogin.com
ADOBE_IMS_USERINFO_URL=https://ims-na1-stg1.adobelogin.com/ims/userinfo/v2
```

### Adding Scopes

To request additional permissions, update the OAuth scopes:
```
openid profile email address phone
```

### Server Configuration

You can customize the server host and port:

```env
HOST=0.0.0.0
PORT=8080
```

## Production Deployment

### Security Checklist

- ✅ Use HTTPS (required for production)
- ✅ Keep `.env` file secure (never commit)
- ✅ Use environment variables in production
- ✅ Configure proper CORS if needed
- ✅ Set up logging and monitoring
- ✅ Use a reverse proxy (nginx, Caddy)
- ✅ Keep dependencies updated

### Example nginx Configuration

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SSE specific settings for /mcp endpoint
    location /mcp {
        proxy_pass http://localhost:8000/mcp;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
    }
}
```

## Testing Without ChatGPT

You can test the server manually using the MCP protocol:

```python
# test_mcp_client.py
import asyncio
import httpx

async def test():
    # Get your Adobe access token (from OAuth flow)
    token = "your_adobe_access_token"
    
    # Call the MCP endpoint
    # This is a simplified example - real MCP requires proper protocol
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/mcp",
            json={
                "method": "tools/call",
                "params": {
                    "name": "hello_user",
                    "arguments": {
                        "access_token": token
                    }
                }
            }
        )
        print(response.json())

asyncio.run(test())
```

## Next Steps

Once you have the basic integration working:

1. **Extend the Tools**
   - Add more MCP tools to the server
   - Integrate with other Adobe APIs
   - Create custom workflows

2. **Improve Error Handling**
   - Add retry logic
   - Better error messages
   - Logging and monitoring

3. **Scale the Deployment**
   - Use load balancers
   - Add caching
   - Implement rate limiting

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Adobe IMS Documentation](https://developer.adobe.com/developer-console/docs/guides/authentication/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [ChatGPT Custom GPTs](https://help.openai.com/en/articles/8554407-gpts-faq)

## Support

For issues with:
- **This MCP server**: Check the GitHub repository
- **Adobe OAuth**: See [Adobe Developer Console](https://developer.adobe.com/console)
- **ChatGPT integration**: See [OpenAI Help Center](https://help.openai.com/)
