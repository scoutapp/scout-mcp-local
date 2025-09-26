"""Used by MCP Inspector for development connection."""
import logging
import os
import sys

from scout_mcp import server


def load_key():
    """Initialize Scout APM client with API key from environment."""
    api_key = os.getenv("SCOUT_API_KEY")
    if not api_key:
        raise ValueError("SCOUT_API_KEY environment variable is required")
    return api_key


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - [%(levelname)s] %(name)s -  - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)

# For local inspector
server.api_client.api_key = load_key()
mcp = server.mcp
