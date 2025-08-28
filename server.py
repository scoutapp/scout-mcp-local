#!/usr/bin/env python3
"""
Scout APM MCP Server

An MCP server that provides tools for querying Scout APM performance data.
Allows users to ask questions about endpoint performance, latency trends, and more.
"""

import logging
import sys

from mcp.server.fastmcp import FastMCP


# Create the MCP server
server = FastMCP("scout-apm-local")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)


def main():
    """Main entry point for the MCP server."""
    try:
        server.run(transport="stdio")
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
