# Scout Monitoring MCP

This repository contains code to locally run an MCP server that can access Scout
Monitoring data via Scout's API. We provide a Docker image that can be pulled and run by
your AI Assistant to access Scout Monitoring data.

This puts Scout Monitoring's performance and error data directly in the hands of your AI Assistant.
For Rails, Django, FastAPI, Laravel and more. Use it to get traces and errors with line-of-code information
that the AI can use to target fixes right in your editor and codebase. N+1 queries, slow endpoints,
slow queries, memory bloat, throughput issues - all your favorite performance problems surfaced
and explained right where you are working.

## Prerequisites

You will need to have or create a Scout Monitoring account and obtain an API key.
1. [Sign up](https://scoutapm.com/users/sign_up)
2. Install the Scout Agent in your application and send Scout data!
    - [Ruby](https://scoutapm.com/docs/ruby/setup)
    - [Python](https://scoutapm.com/docs/python/setup)
    - [PHP](https://scoutapm.com/docs/php)
    - If you are trying this out locally, make sure `monitor: true`, `errors_enabled: true`
      are set in your config for the best experience
2. Visit [settings](https://scoutapm.com/settings) to get or create an API key
2. Install Docker. Instructions below assume you can start a Docker container

**The MCP server will not currently start without an API key set, either in the
environment or by a command-line argument on startup.**

## Installation

We recommend using the provided Docker image to run the MCP server.
It is intended to be started by your AI Assistant and configured with your Scout API
key. Many local clients allow specifying a command to run the MCP server in some
location. A few examples are provided below.

The Docker image is available on [Docker Hub](https://hub.docker.com/r/scoutapp/scout-mcp-local).

Of course, you can always clone this repo and run the MCP server directly; `uv` or other
environment management tools are recommended.


### Configure a local Client (e.g. Claude Code)

Usually this just means supplying a command to run the MCP server with your API key in the environment
to your AI Assistant's config. Here is the shape of the JSON (the top-level key varies):

```json
{
  "mcpServers": {
    "scout-apm": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env", "SCOUT_API_KEY", "scoutapp/scout-mcp-local"],
      "env": { "SCOUT_API_KEY": "your_scout_api_key_here"}
    }
  }
}
```

#### Claude Code
1. Copy the inner object above and paste it into `./scoutapm.json` or somewhere
   convenient
    - `{"command": "docker", "args": ["run", "--rm", "-i", "--env", "SCOUT_API_KEY=your_scout_api_key_here", "scoutapp/scout-mcp-local"], "env": {}}`
2. Update the `SCOUT_API_KEY` value to your actual api key
3. `claude mcp add-json scoutmcp "$(cat ./scoutmcp.json)"`

#### Cursor
[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=scout-apm&config=eyJjb21tYW5kIjoiZG9ja2VyIHJ1biAtLXJtIC1pIC0tZW52IFNDT1VUX0FQSV9LRVk9JFBVVF9ZT1VSX0tFWV9IRVJFIHNjb3V0YXBwL3Njb3V0LW1jcC1sb2NhbCIsImVudiI6e319)

MAKE SURE to update the `SCOUT_API_KEY` value to your actual api key in
  `Arguments` in the Cursor Settings > MCP

#### VS Code Copilot
- [VS Code Copilot docs](https://code.visualstudio.com/docs/copilot/customization/mcp-servers#_add-an-mcp-server)
    - We recommend the "Add an MCP server to your workspace" option

#### Claude Desktop
Add above JSON to config:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`


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

