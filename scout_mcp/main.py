#!/usr/bin/env python3
"""
Scout APM MCP Server

An MCP server that provides tools for querying Scout APM performance data.
Allows users to ask questions about endpoint performance, latency trends, and more.
"""

import argparse
import logging
import os
import sys

from . import server


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Scout APM MCP Server")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    parser.add_argument("--api-key", help="Scout APM API Key")

    return parser.parse_args()


def init_logging(level: int):
    logging.basicConfig(
        level=level,
        format="%(asctime)s - [%(levelname)s] %(name)s -  - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def load_key(args: argparse.Namespace):
    """
    Initialize Scout APM client with API key from environment or args. Prefers CLI arg.
    """
    if args.api_key:
        return args.api_key

    api_key = os.getenv("SCOUT_API_KEY")
    if not api_key:
        raise ValueError("SCOUT_API_KEY environment variable is required")
    return api_key


def main():
    """Main entry point for the MCP server."""
    args = parse_args()
    init_logging(getattr(logging, args.log_level.upper()))
    server.api_client.api_key = load_key(args)
    try:
        server.mcp.run(transport="stdio")
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
