import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import scout_api

log = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("scout-apm-local")

api_client = scout_api.ScoutAPMAsync("")


def format_time_series_for_js(data: dict[str, list]) -> str:
    """Format time series data for JavaScript visualization."""
    js_data = {}
    for metric, series in data.items():
        js_data[metric] = [
            {"timestamp": timestamp, "value": value} for timestamp, value in series
        ]
    return json.dumps(js_data, indent=2)


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values."""
    if old_value == 0:
        return 100.0 if new_value > 0 else 0.0
    return ((new_value - old_value) / old_value) * 100


@mcp.resource("scoutapm://metrics")
def list_available_metrics() -> set[str]:
    """List all available metrics for the Scout APM API."""
    return scout_api.VALID_METRICS


@mcp.tool(name="list_apps")
async def list_scout_apps() -> list[dict[str, Any]]:
    """List available Scout APM applications."""
    global log
    log.info("Fetching list of Scout APM applications")
    log.info(f"Using API key: {api_client.api_key[:4] + '...'}")
    try:
        async with api_client as scout_client:
            apps = await scout_client.get_apps()
        return apps
    except scout_api.ScoutAPMError as e:
        return [{"error": str(e)}]


@mcp.tool(name="get_app_metrics")
async def get_app_metric(app_id: int, metric: str, days: int = 7) -> dict[str, Any]:
    """Get metric data for a specific application."""
    try:
        async with api_client as scout_client:
            data = await scout_client.get_metric_data_range(app_id, metric, days)
    except scout_api.ScoutAPMError as e:
        return {"error": str(e)}

    if metric not in data or not data[metric]:
        return {"error": f"No data available for metric {metric}"}

    series = data[metric]
    return {
        "app_id": app_id,
        "metric": metric,
        "timeframe_days": days,
        "data_points": len(series),
        "series": series,
    }
