# Scout Monitoring MCP

This repository contains code to locally run an MCP server that can access Scout
Monitoring data via Scout's API. We provide a Docker image that can be pulled and run by
your AI Assistant to access Scout Monitoring data.

## Prerequisites

You will need to have or create a Scout Monitoring account and obtain an API key.
[Sign up](https://scoutapm.com/users/sign_up) and get your API key from the Scout
[settings](https://scoutapm.com/settings).

## Installation

The Docker image is available on [Docker Hub](https://hub.docker.com/r/scoutapp/scout-mcp-local).


### Configure a local Client (e.g. Claude Desktop)

Usually this just means supplying a command to run the MCP server with your API key in the environment
to your AI Assistant's config.

Add to your Claude Desktop config:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "scout-apm": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env", "SCOUT_API_KEY=your_scout_api_key_here", "scoutapp/scout-mcp-local"],
      "env": {}
    }
  }
}
```

### Token Usage

We are currently more interested in expanding available information than strictly
controlling response size from our MCP tools. If your AI Assistant has a configurable
token limit (e.g. Claude Code `export MAX_MCP_OUTPUT_TOKENS=50000`), we recommend
setting it generously high, e.g. 50,000 tokens.


## Usage

Scout's MCP is intended to put error and performance data directly in the... hands? of your AI Assistant.
Use it to get traces and errors with line-of-code information that the AI can use to target
fixes right in your editor.


## Useful Prompts

- "Summarize the available tools in the Scout Monitoring MCP."
- "Find the slowest endpoints for app `my-app-name` in the last 7 days."
- "Show me the highest-frequency errors for app Foo in the last 24 hours."
- "Get any recent n+1 queries for app Bar"


## Local Development

### Run with Inspector
```bash
uv run task dev
```
Connect within inspector to add API key, set to STDIO transport

### Build the Docker image
```bash
docker build -t scout-mcp-local .
```

