# Scout Monitoring MCP

This repository contains code to locally run an MCP server that can access Scout
Monitoring data via Scout's API. We provide a Docker image that can be pulled and run by
your AI Assistant to access Scout Monitoring data.

## Tools

### List Apps
### Get App Errors
### Get App Metrics
### Get App Endpoints
### Get Endpoint Metrics
### Get Endpoint Traces

## Local Development

### Run with Inspector
```bash
uv run mcp dev server.py
```
Connect within inspector to add API key, set to STDIO transport

### Build the Docker image
```bash
docker build -t scout-mcp-local .
```

### 2. Configure a local CLient (e.g. Claude Desktop)
Add to your Claude Desktop config:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "scout-apm": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env", "SCOUT_API_KEY=your_scout_api_key_here", "scout-mcp-local"],
      "env": {}
    }
  }
}
```
