# Scout Monitoring MCP

This repository contains code to locally run an MCP server that can access [Scout
Monitoring](https://www.scoutapm.com) data via Scout's API. We provide a Docker image that can be pulled and run by
your AI Assistant to access Scout Monitoring data.

<a href="https://glama.ai/mcp/servers/@scoutapp/scout-mcp-local">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@scoutapp/scout-mcp-local/badge" alt="Scout Monitoring MCP server" />
</a>

This puts Scout Monitoring's performance and error data directly in the hands of your AI Assistant.
For Rails, Django, FastAPI, Laravel and more. Use it to get traces and errors with line-of-code information
that the AI can use to target fixes right in your editor and codebase. N+1 queries, slow endpoints,
slow queries, memory bloat, throughput issues - all your favorite performance problems surfaced
and explained right where you are working.

**If this makes your life a tiny bit better, why not :star: it?!**

## Setup Wizard

The simplest way to configure and start using the Scout MCP is with our interactive setup wizard.
It handles all the prereqs and installation steps for you.

Run via npx:
```bash
npx @scout_apm/wizard
```

Build and run from source:
```bash
cd ./wizard
npm install
npm run build
node dist/wizard.js
```

The wizard will guide you through:
- Selecting your AI coding platform (Cursor, Claude Code, Claude Desktop)
- Entering your Scout API key
- Automatically configuring the MCP server settings

#### Supported Platforms

The wizard currently supports setup for:
- **Cursor** - Automatically configures MCP settings
- **Claude Code (CLI)** - Provides the correct command to run
- **Claude Desktop** - Updates the configuration file for Windows/Mac

For all others, it will output JSON that you can copy/paste into your AI Assistant's MCP configuration.

## Prerequisites

The Wizard is a great way to get started, but you can also set things up manually.
You will need to have or create a Scout Monitoring account and obtain an API key.

1. [Sign
   up](https://scoutapm.com/users/sign_up?utm_source=github&utm_medium=github&utm_campaign=scout-mcp-local)
2. Install the Scout Agent in your application and send Scout data!
    - [Ruby](https://scoutapm.com/docs/ruby/setup)
    - [Python](https://scoutapm.com/docs/python/setup)
    - [PHP](https://scoutapm.com/docs/php)
    - If you are trying this out locally, make sure `monitor: true`, `errors_enabled: true`
      are set in your config for the best experience
2. Visit [settings](https://scoutapm.com/settings) to get or create an API key
    - This is _not_ your "Agent Key"; it's the "API Key" that can be created on the
      Settings page
    - This is a read-only key that can only access data in your account
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

### Configure a local Client (e.g. Claude/Cursor/VS Code Copilot)

If you would like to configure the MCP manually, this usually just means supplying a command to run the MCP server with your API key in the environment
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

<details>
<summary> Claude Code</summary>

```sh
claude mcp add scoutmcp -e SCOUT_API_KEY=your_scout_api_key_here -- docker run --rm -i -e SCOUT_API_KEY scoutapp/scout-mcp-local
```
</details>

<details>
<summary>Cursor</summary>

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=scout-apm&config=eyJjb21tYW5kIjoiZG9ja2VyIHJ1biAtLXJtIC1pIC0tZW52IFNDT1VUX0FQSV9LRVkgc2NvdXRhcHAvc2NvdXQtbWNwLWxvY2FsIiwiZW52Ijp7IlNDT1VUX0FQSV9LRVkiOiJ5b3VyX3Njb3V0X2FwaV9rZXlfaGVyZSJ9fQ%3D%3D)

MAKE SURE to update the `SCOUT_API_KEY` value to your actual api key in
  `Arguments` in the Cursor Settings > MCP
</details>

<details>
<summary>VS Code Copilot</summary>

- [VS Code Copilot docs](https://code.visualstudio.com/docs/copilot/customization/mcp-servers#_add-an-mcp-server)
    - We recommend the "Add an MCP server to your workspace" option
</details>

<details>
<summary>Claude Desktop</summary>

Add the following to your claude config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

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

</details>




## Using the Scout Monitoring MCP

Scout's MCP is intended to put error and performance data directly in the... hands? of your AI Assistant.
Use it to get traces and errors with line-of-code information that the AI can use to target
fixes right in your editor.

Most assistants will show you both raw tool calls and perform analysis. Desktop assistants
can readily create custom JS applications to explore whatever data you desire.
Assistants integrated into code editors can use trace data and error backtraces to make
fixes right in your codebase.

Combine Scout's MCP with your AI Assistant's other tools to:

- Create rich GitHub/GitLab issues based on errors and performance data
- Make JIRA fun - have your AI Assistant create tickets with all the details
- Generate PRs that fix specific errors and performance problems

### Tools

The Scout MCP provides the following tools for accessing Scout APM data:

- **`list_apps`** - List available Scout APM applications, with optional filtering by last active date
- **`get_app_metrics`** - Get individual metric data (response_time, throughput, etc.) for a specific application
- **`get_app_endpoints`** - Get all endpoints for an application with aggregated performance metrics
- **`get_endpoint_metrics`** - Get timeseries metrics for a specific endpoint in an application
- **`get_app_endpoint_traces`** - Get recent traces for an app filtered to a specific endpoint
- **`get_app_trace`** - Get an individual trace with all spans and detailed execution information
- **`get_app_error_groups`** - Get recent error groups for an app, optionally filtered by endpoint
- **`get_app_insights`** - Get performance insights including N+1 queries, memory bloat, and slow queries

### Resources

The Scout MCP provides configuration templates as resources that your AI assistant can read and apply:

- **`scoutapm://config-resources/{framework}`** - Setup instructions for supported framework or library (rails, django, flask, fastapi)
- **`scoutapm://config-resources/list`** - List all available configuration templates
- **`scoutapm://metrics`** - List of all available metrics for Scout APM


### Useful Prompts

#### Setup & Configuration
- "Help me set up Scout monitoring for my Rails application"
- "Create a Scout APM config file for my Django project with key ABC123"

#### Performance & Monitoring
- "Summarize the available tools in the Scout Monitoring MCP."
- "Find the slowest endpoints for app `my-app-name` in the last 7 days. Generate a table
  with the results including the average response time, throughput, and P95 response time."
- "Show me the highest-frequency errors for app `Foo` in the last 24 hours. Get the
  latest error detail, examine the backtrace and suggest a fix."
- "Get any recent n+1 insights for app `Bar`. Pull the specific trace by id and help me
  optimize it based on the backtrace data."

### Token Usage

We are currently more interested in expanding available information than strictly
controlling response size from our MCP tools. If your AI Assistant has a configurable
token limit (e.g. Claude Code `export MAX_MCP_OUTPUT_TOKENS=50000`), we recommend
setting it generously high, e.g. 50,000 tokens.

## Local Development

We use `uv` and `taskipy` to manage environments and run tasks for this project.

### Run with Inspector
```bash
uv run task dev
```
Connect within inspector to add API key, set to STDIO transport

### Build the Docker image
```bash
docker build -t scout-mcp-local .
```

## Release

1. Branch and bump versions with `uv run python bump_versions.py`
1. Get that merged
1. Create a GitHub release with the new version (`gh release create v2025.11.3 --generate-notes --draft`)

For the bots:

mcp-name: com.scoutapm/scout-mcp-local
