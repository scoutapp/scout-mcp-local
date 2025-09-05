# 2025-09-04T11:00:00Z
import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import scout_api

log = logging.getLogger(__name__)

mcp = FastMCP("scout-apm-local")

api_client = scout_api.ScoutAPMAsync()


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
    log.info("Fetching list of Scout APM applications")
    log.info(f"Using API key: {api_client.api_key[:4] + '...'}")
    try:
        async with api_client as scout_client:
            apps = await scout_client.get_apps()
        return apps
    except scout_api.ScoutAPMError as e:
        return [{"error": str(e)}]


@mcp.tool(name="get_app_metrics")
async def get_app_metric(
    app_id: int, metric: str, from_: str, to: str
) -> dict[str, Any]:
    """Get individual metric data for a specific application.

    Args:
        app_id (int): The ID of the Scout APM application.
        metric (str): The metric to retrieve (e.g., "response_time", "throughput").
        from_ (str): The start datetime in ISO 8601 format.
        to (str): The end datetime in ISO 8601 format.

    """
    if metric not in scout_api.VALID_METRICS:
        return {
            "error": f"Invalid metric '{metric}'. "
            f"Valid metrics are: {', '.join(scout_api.VALID_METRICS)}"
        }
    try:
        async with api_client as scout_client:
            data = await scout_client.get_metric_data(app_id, metric, from_, to)
    except scout_api.ScoutAPMError as e:
        return {"error": str(e)}

    if metric not in data or not data[metric]:
        return {"error": f"No data available for metric {metric}"}

    series = data[metric]
    return {
        "app_id": app_id,
        "metric": metric,
        "duration": f"{from_} to {to}",
        "data_points": len(series),
        "series": series,
    }


@mcp.tool(name="get_app_endpoints")
async def get_app_endpoints(app_id: int, from_: str, to: str) -> list[dict[str, Any]]:
    """
    Get all endpoints for a specific application. Also gets aggregated performance
    metrics withing the window of "from_" to "to". Useful for identifying high
    throughput, high latency or high error rate endpoints accross the application with a
    single call.

    These endpoints can be used in other tools to fetch endpoint-specific metrics,
    traces or errors.

    Args:
        app_id (int): The ID of the Scout APM application.
        from_ (str): The start datetime in ISO 8601 format.
        to (str): The end datetime in ISO 8601 format.
    """
    try:
        duration = scout_api.make_duration(from_, to)
        async with api_client as scout_client:
            endpoints = await scout_client.get_endpoints(app_id, duration)
        return endpoints
    except scout_api.ScoutAPMError as e:
        return [{"error": str(e)}]


@mcp.tool(name="get_endpoint_metrics")
async def get_endpoint_metric(
    app_id: int, endpoint: str, metric: str, from_: str, to: str
) -> dict[str, Any]:
    """
    Get a single timeseries metric for a specific endpoint in an application.

    Args:
        app_id (int): The ID of the Scout APM application.
        endpoint (str): The endpoint path (e.g., "/users", "/orders").
        metric (str): The metric to retrieve (e.g., "response_time", "throughput").
        from_ (str): The start datetime in ISO 8601 format.
        to (str): The end datetime in ISO 8601 format.
    """
    try:
        duration = scout_api.make_duration(from_, to)
        async with api_client as scout_client:
            data = await scout_client.get_endpoint_metric(
                app_id, endpoint, metric, duration
            )
    except Exception as e:
        return {"error": str(e)}

    if metric not in data or not data[metric]:
        return {
            "error": f"No data available for endpoint {endpoint} and metric {metric}"
        }

    series = data[metric]
    return {
        "app_id": app_id,
        "endpoint": endpoint,
        "metric": metric,
        "duration": f"{from_} to {to}",
        "data_points": len(series),
        "series": series,
    }


@mcp.tool(name="get_app_endpoint_traces")
async def get_app_endpoint_traces(
    app_id: int, endpoint_id: str | None, from_: str, to: str
) -> list[dict[str, Any]]:
    """
    Get recent traces for an app, optionally filtered to a specific endpoint.

    Args:
        app_id (int): The ID of the Scout APM application.
        endpoint_id (str | None): The ID of the endpoint to filter traces. If None,
            fetches all traces for the app.
        from_ (str): The start datetime in ISO 8601 format.
        to (str): The end datetime in ISO 8601 format.
    """
    try:
        async with api_client as scout_client:
            traces = await scout_client.get_traces(app_id, endpoint_id)
        return traces
    except scout_api.ScoutAPMError as e:
        return [{"error": str(e)}]


@mcp.tool(name="get_app_error_groups")
async def get_app_error_groups(
    app_id: int, endpoint_id: str | None = None
) -> list[dict[str, Any]]:
    """
    Get recent error_groups for an app, optionally filtered to a specific endpoint.

    Args:
        app_id (int): The ID of the Scout APM application.
        endpoint_id (str | None): The ID of the endpoint to filter errors. If None,
            fetches all errors for the app.
    """
    try:
        async with api_client as scout_client:
            errors = await scout_client.get_error_groups(app_id, endpoint_id)
        return errors
    except scout_api.ScoutAPMError as e:
        return [{"error": str(e)}]
