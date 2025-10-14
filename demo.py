"""
Example script demonstrating the OAuth flow and tool usage.

This shows how ChatGPT (or any MCP client) would interact with the server.
Note: This is a demonstration script that doesn't require any external dependencies.
"""

import asyncio


async def demo_oauth_flow():
    """
    Demonstrate the complete OAuth flow.
    
    This is what happens when ChatGPT connects to the MCP server:
    """
    print("=" * 70)
    print("OAuth Flow Demonstration")
    print("=" * 70)
    
    # Step 1: ChatGPT discovers OAuth metadata
    print("\n[Step 1] ChatGPT fetches OAuth metadata")
    print("GET http://localhost:8000/.well-known/oauth-authorization-server")
    print("Response: OAuth endpoints and configuration")
    
    # Step 2: User authorization
    print("\n[Step 2] User is redirected to Adobe IMS for authorization")
    print("URL: https://ims-na1.adobelogin.com/ims/authorize/v2")
    print("Parameters:")
    print("  - client_id: <your_client_id>")
    print("  - response_type: code")
    print("  - scope: openid profile email")
    print("  - redirect_uri: <chatgpt_callback>")
    
    # Step 3: User grants permission
    print("\n[Step 3] User signs in to Adobe and grants permissions")
    print("Adobe redirects back with authorization code")
    
    # Step 4: Token exchange
    print("\n[Step 4] ChatGPT exchanges authorization code for access token")
    print("POST https://ims-na1.adobelogin.com/ims/token/v3")
    print("Response: access_token, refresh_token, expires_in")
    
    # Step 5: Use the tool
    print("\n[Step 5] ChatGPT calls the MCP tool with the access token")
    print("Tool: hello_user")
    print("Parameter: access_token=<adobe_access_token>")
    print("Expected result: 'Hello, John Doe! 👋'")


async def demo_server_endpoints():
    """Demonstrate server endpoints (conceptual)."""
    print("\n" + "=" * 70)
    print("Server Endpoints")
    print("=" * 70)
    
    endpoints = [
        {
            "method": "GET",
            "path": "/health",
            "description": "Health check endpoint",
            "response": '{"status": "healthy", "service": "Adobe OAuth MCP Server"}'
        },
        {
            "method": "GET",
            "path": "/.well-known/oauth-authorization-server",
            "description": "OAuth metadata (RFC 8414)",
            "response": '{"issuer": "https://ims-na1.adobelogin.com", ...}'
        },
        {
            "method": "POST/SSE",
            "path": "/mcp",
            "description": "MCP protocol endpoint (Server-Sent Events)",
            "response": "MCP protocol messages"
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n{endpoint['method']} {endpoint['path']}")
        print(f"  Description: {endpoint['description']}")
        print(f"  Response: {endpoint['response']}")


async def demo_tool_usage():
    """Demonstrate the hello_user tool."""
    print("\n" + "=" * 70)
    print("MCP Tool: hello_user")
    print("=" * 70)
    
    print("\nTool Definition:")
    print("  Name: hello_user")
    print("  Description: Get a personalized greeting using your name from Adobe")
    print("  Parameters:")
    print("    - access_token (string, required): OAuth access token from Adobe IMS")
    print("  Returns: A personalized greeting message")
    
    print("\nExecution Flow:")
    print("  1. Receive access_token from ChatGPT")
    print("  2. Verify token with Adobe IMS")
    print("  3. Fetch user info from Adobe UserInfo endpoint")
    print("  4. Extract user's name")
    print("  5. Return personalized greeting")
    
    print("\nExample with valid token:")
    print("  Input: access_token='eyJhbGc...'")
    print("  Process:")
    print("    - Token verified ✓")
    print("    - User info retrieved: {name: 'John Doe', email: 'john@example.com'}")
    print("  Output: 'Hello, John Doe! 👋'")
    
    print("\nExample with invalid token:")
    print("  Input: access_token='invalid_token'")
    print("  Output: 'Error: Invalid or expired access token'")


async def main():
    """Main demonstration function."""
    print("\n🚀 Adobe OAuth MCP Server - Integration Demo\n")
    
    # Show the OAuth flow
    await demo_oauth_flow()
    
    # Show server endpoints
    await demo_server_endpoints()
    
    # Show tool usage
    await demo_tool_usage()
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print("""
This demonstration showed:

1. How ChatGPT discovers and uses OAuth with the MCP server
2. The complete authorization flow with Adobe IMS
3. The API endpoints available on the server
4. How the hello_user tool works

To see this in action:
1. Install dependencies: pip install -r requirements.txt
2. Configure .env with your Adobe OAuth credentials
3. Start the server: python server.py
4. Configure ChatGPT with the MCP endpoint: http://localhost:8000/mcp
5. Authorize with your Adobe account
6. Use the hello_user tool to get a personalized greeting

The server will:
- Verify your access token with Adobe IMS
- Fetch your user information from Adobe
- Return "Hello, [Your Name]! 👋"

For testing the server locally:
- Health check: curl http://localhost:8000/health
- OAuth metadata: curl http://localhost:8000/.well-known/oauth-authorization-server
    """)


if __name__ == "__main__":
    asyncio.run(main())
