#!/usr/bin/env python3
"""
Setup verification script for Adobe OAuth MCP Server.

This script helps verify that your environment is properly configured
before running the server.
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_status(check, status, message=""):
    """Print a status line."""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {check}: {'OK' if status else 'FAIL'}")
    if message:
        print(f"   → {message}")


def check_python_version():
    """Check if Python version is 3.9 or higher."""
    version = sys.version_info
    required = (3, 9)
    status = version >= required
    
    print_status(
        "Python Version",
        status,
        f"Found {version.major}.{version.minor}.{version.micro}" +
        ("" if status else f" (Required: {required[0]}.{required[1]}+)")
    )
    return status


def check_file_exists(filepath, description):
    """Check if a file exists."""
    path = Path(filepath)
    exists = path.exists()
    print_status(description, exists, str(path) if exists else f"{filepath} not found")
    return exists


def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = Path(".env")
    
    if not env_path.exists():
        print_status(".env file", False, "Create it using: cp .env.example .env")
        return False
    
    print_status(".env file", True, "File exists")
    
    # Check for required variables
    required_vars = [
        "ADOBE_CLIENT_ID",
        "ADOBE_CLIENT_SECRET",
        "ADOBE_IMS_BASE_URL",
        "ADOBE_IMS_USERINFO_URL",
    ]
    
    with open(env_path) as f:
        content = f.read()
    
    all_present = True
    for var in required_vars:
        present = var in content
        if not present:
            all_present = False
        
        # Check if it has a value (not just "your_xxx_here")
        if present:
            for line in content.split('\n'):
                if line.startswith(var + "="):
                    value = line.split('=', 1)[1].strip()
                    has_value = value and "your_" not in value.lower()
                    print_status(f"  {var}", has_value, 
                               "Set" if has_value else "Needs configuration")
                    if not has_value:
                        all_present = False
                    break
    
    return all_present


def check_dependencies():
    """Check if required Python packages are installed."""
    packages = [
        "fastapi",
        "uvicorn",
        "fastmcp",
        "python-dotenv",
        "httpx",
        "pydantic",
        "pydantic_settings",
    ]
    
    all_installed = True
    for package in packages:
        try:
            __import__(package if package != "python-dotenv" else "dotenv")
            print_status(f"  {package}", True, "Installed")
        except ImportError:
            print_status(f"  {package}", False, "Not installed")
            all_installed = False
    
    if not all_installed:
        print("\n   To install all dependencies:")
        print("   pip install -r requirements.txt")
    
    return all_installed


def check_port_available(port=8000):
    """Check if the port is available."""
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        available = result != 0
        print_status(
            f"Port {port}",
            available,
            "Available" if available else f"Already in use"
        )
        return available
    except Exception as e:
        print_status(f"Port {port}", False, f"Error checking: {e}")
        return False


def verify_adobe_endpoints():
    """Verify Adobe IMS endpoints are reachable."""
    print("\nNote: Adobe endpoint verification requires network access")
    print("      and httpx package. Skipping for now.")
    return True


def main():
    """Main verification function."""
    print_header("Adobe OAuth MCP Server - Setup Verification")
    
    print("\n📋 Checking Prerequisites...")
    
    checks = {
        "python_version": check_python_version(),
        "requirements_txt": check_file_exists("requirements.txt", "requirements.txt"),
        "server_py": check_file_exists("server.py", "server.py"),
        "env_example": check_file_exists(".env.example", ".env.example"),
    }
    
    print("\n📝 Checking Configuration...")
    checks["env_file"] = check_env_file()
    
    print("\n📦 Checking Dependencies...")
    checks["dependencies"] = check_dependencies()
    
    print("\n🔌 Checking Network...")
    checks["port"] = check_port_available(8000)
    
    # Summary
    print_header("Summary")
    
    total = len(checks)
    passed = sum(checks.values())
    
    print(f"\nChecks passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All checks passed! You're ready to start the server:")
        print("\n   python server.py")
        print("\n   Server will be available at: http://localhost:8000")
        print("   MCP endpoint: http://localhost:8000/mcp")
        return 0
    else:
        print("\n❌ Some checks failed. Please review the issues above.")
        
        print("\n📚 Quick Fixes:")
        
        if not checks.get("env_file"):
            print("\n1. Create and configure .env file:")
            print("   cp .env.example .env")
            print("   # Edit .env with your Adobe credentials")
        
        if not checks.get("dependencies"):
            print("\n2. Install dependencies:")
            print("   pip install -r requirements.txt")
        
        if not checks.get("port"):
            print("\n3. Stop the process using port 8000 or change PORT in .env")
        
        print("\n📖 For detailed setup instructions, see:")
        print("   - README.md")
        print("   - QUICKSTART.md")
        print("   - CHATGPT_INTEGRATION.md")
        
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
