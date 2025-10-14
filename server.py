"""
MCP Server with Adobe OAuth Integration

This server implements the MCP (Model Context Protocol) with OAuth support for Adobe IMS.
It provides a tool that fetches user information from Adobe and returns a personalized greeting.
"""

import os
import httpx
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastmcp import FastMCP
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    adobe_client_id: str = os.getenv("ADOBE_CLIENT_ID", "")
    adobe_client_secret: str = os.getenv("ADOBE_CLIENT_SECRET", "")
    adobe_ims_base_url: str = os.getenv("ADOBE_IMS_BASE_URL", "https://ims-na1.adobelogin.com")
    adobe_ims_userinfo_url: str = os.getenv("ADOBE_IMS_USERINFO_URL", "https://ims-na1.adobelogin.com/ims/userinfo/v2")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))


settings = Settings()

# Initialize FastMCP
mcp = FastMCP("Adobe OAuth MCP Server")


class AdobeOAuthService:
    """Service for handling Adobe OAuth operations."""
    
    def __init__(self):
        self.client_id = settings.adobe_client_id
        self.client_secret = settings.adobe_client_secret
        self.ims_base_url = settings.adobe_ims_base_url
        self.userinfo_url = settings.adobe_ims_userinfo_url
    
    async def verify_token(self, access_token: str) -> bool:
        """
        Verify the access token against Adobe IMS.
        
        Args:
            access_token: The OAuth access token to verify
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                # Verify token by calling the userinfo endpoint
                response = await client.get(
                    self.userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Token verification error: {e}")
            return False
    
    async def get_user_info(self, access_token: str) -> dict:
        """
        Fetch user information from Adobe IMS.
        
        Args:
            access_token: The OAuth access token
            
        Returns:
            dict: User information including name, email, etc.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch user info: {response.text}"
                )
            
            return response.json()


oauth_service = AdobeOAuthService()


@mcp.tool()
async def hello_user(access_token: str) -> str:
    """
    Get a personalized greeting using the user's name from Adobe.
    
    This tool verifies the OAuth token with Adobe IMS, fetches the user's
    information, and returns a personalized greeting.
    
    Args:
        access_token: OAuth access token from Adobe IMS
        
    Returns:
        str: A personalized greeting message
    """
    # Verify the token
    is_valid = await oauth_service.verify_token(access_token)
    if not is_valid:
        return "Error: Invalid or expired access token"
    
    try:
        # Get user information
        user_info = await oauth_service.get_user_info(access_token)
        
        # Extract name from user info
        name = user_info.get("name", "")
        if not name:
            # Try to construct name from first and last name
            first_name = user_info.get("first_name", "")
            last_name = user_info.get("last_name", "")
            name = f"{first_name} {last_name}".strip()
        
        if not name:
            name = user_info.get("email", "User")
        
        return f"Hello, {name}! 👋"
    except Exception as e:
        return f"Error fetching user information: {str(e)}"


# Create FastAPI app
app = FastAPI(
    title="Adobe OAuth MCP Server",
    description="MCP Server with Adobe OAuth integration for personalized greetings",
    version="1.0.0"
)


# Add OAuth configuration to the app
@app.get("/.well-known/oauth-authorization-server")
async def oauth_metadata():
    """
    OAuth authorization server metadata endpoint.
    
    This endpoint provides OAuth configuration according to RFC 8414.
    """
    return {
        "issuer": settings.adobe_ims_base_url,
        "authorization_endpoint": f"{settings.adobe_ims_base_url}/ims/authorize/v2",
        "token_endpoint": f"{settings.adobe_ims_base_url}/ims/token/v3",
        "userinfo_endpoint": settings.adobe_ims_userinfo_url,
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Adobe OAuth MCP Server"}


# Mount MCP routes with SSE transport
# The FastMCP library automatically handles the MCP protocol
app.mount("/mcp", mcp.get_asgi_app())


if __name__ == "__main__":
    import uvicorn
    
    print(f"Starting Adobe OAuth MCP Server...")
    print(f"Server will be available at http://{settings.host}:{settings.port}")
    print(f"MCP endpoint: http://{settings.host}:{settings.port}/mcp")
    print(f"OAuth metadata: http://{settings.host}:{settings.port}/.well-known/oauth-authorization-server")
    
    uvicorn.run(
        "server:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
