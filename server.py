#!/usr/bin/env python3
"""
Scout APM MCP Server

An MCP server that provides tools for querying Scout APM performance data.
Allows users to ask questions about endpoint performance, latency trends, and more.
"""

import logging
import os
import sys

from app import server

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)


def load_key():
    """Initialize Scout APM client with API key from environment."""
    api_key = os.getenv("SCOUT_API_KEY")
    if not api_key:
        raise ValueError("SCOUT_API_KEY environment variable is required")
    return api_key


# For local inspector
server.api_client.api_key = load_key()
mcp = server.mcp


def main():
    """Main entry point for the MCP server."""
    try:
        server.mcp.run(transport="stdio")
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
