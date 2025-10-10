# 2025-09-04T11:00:00Z
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
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


@mcp.resource("scoutapm://config-resources/{library_name}")
def get_config_resource(library_name: str) -> str:
    """Get the Scout APM setup instructions and configuration for a specific library or framework.
    
    Supported configurations:
    
    Web Frameworks:
    - bottle: Bottle web framework
    - dash: Plotly Dash (built on Flask)
    - django: Django web framework
    - falcon: Falcon web framework
    - fastapi: FastAPI (async web framework)
    - flask: Flask web framework
    - hug: Hug API framework
    - rails: Ruby on Rails
    - starlette: Starlette ASGI framework
    
    Background Job Processing:
    - celery: Celery distributed task queue
    - dramatiq: Dramatiq background task processing
    - huey: Huey task queue
    - rq: Redis Queue (RQ)
    
    Database/ORM:
    - sqlalchemy: SQLAlchemy ORM

    """
    templates_dir = Path(__file__).parent / "config_resources"
    template_path = templates_dir / f"{library_name}.md"
    
    if template_path.exists():
        return template_path.read_text()
    else:
        available = [f.stem for f in templates_dir.iterdir() if f.is_file() and f.suffix == ".md"]
        return f"Configuration not found for: {library_name}\n\nAvailable configurations: {', '.join(sorted(available))}"


@mcp.resource("scoutapm://config-resources/list")
def list_config_resources() -> dict[str, str]:
    """List all available Scout APM configuration templates.
    
    Returns a dictionary mapping library/framework names to their resource URIs.
    Use this to discover what configuration guides are available before fetching
    a specific one with scoutapm://config-resources/{library_name}.
    """
    templates_dir = Path(__file__).parent / "config_resources"
    templates = {}
    
    if templates_dir.exists():
        for template_file in templates_dir.iterdir():
            if template_file.is_file() and template_file.suffix == ".md":
                library_name = template_file.stem
                templates[library_name] = f"scoutapm://config-resources/{library_name}"
    
    return templates


@mcp.tool(name="list_apps")
async def list_scout_apps(active_since: str | None = None) -> list[dict[str, Any]]:
    """
    List available Scout APM applications. Provide an optional `active_since` ISO 8601
    to filter to only apps that have reported data since that time. Defaults to the
    metric retention period of thirty days.

    Args:
        active_since (str): ISO 8601 datetime string to filter apps active since that
                            time.
    """
    active_time = (
        scout_api._parse_time(active_since)
        if active_since
        else datetime.now(tz=timezone.utc) - timedelta(days=30)
    )

    def parse_reported_at(reported_at: str) -> datetime:
        parsed = (
            scout_api._parse_time(reported_at)
            if reported_at
            else datetime.min.replace(tzinfo=timezone.utc)
        )
        return parsed

    try:
        async with api_client as scout_client:
            apps = await scout_client.get_apps()

        filtered = [
            app
            for app in apps
            if parse_reported_at(app["last_reported_at"]) >= active_time
        ]
        return filtered
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
            for e in endpoints:
                e["endpoint_id"] = scout_api.get_endpoint_id(e)
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
    app_id: int, from_: str, to: str, endpoint_id: str
) -> list[dict[str, Any]]:
    """
    Get recent traces for an app filtered to a specific endpoint.

    Args:
        app_id (int): The ID of the Scout APM application.
        endpoint_id (str): The ID of the endpoint to filter traces.
        from_ (str): The start datetime in ISO 8601 format.
        to (str): The end datetime in ISO 8601 format.
    """
    try:
        duration = scout_api.make_duration(from_, to)
        async with api_client as scout_client:
            traces = await scout_client.get_endpoint_traces(
                app_id, endpoint_id, duration
            )
        return traces
    except scout_api.ScoutAPMError as e:
        return [{"error": str(e)}]


@mcp.tool(name="get_app_trace")
async def get_app_trace(app_id: int, trace_id: int) -> dict[str, Any]:
    """
    Get an individual trace with all spans.

    Args:
        app_id (int): The ID of the Scout APM application.
        trace_id (int): The ID of the trace to retrieve.
    """
    try:
        async with api_client as scout_client:
            trace = await scout_client.get_trace(app_id, trace_id)
        return trace
    except scout_api.ScoutAPMError as e:
        return {"error": str(e)}


@mcp.tool(name="get_app_error_groups")
async def get_app_error_groups(
    app_id: int,
    from_: str,
    to: str,
    endpoint_id: str | None = None,
    error_group_id: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Get recent error_groups for an app, optionally filtered to a specific endpoint or
    group.

    Args:
        app_id (int): The ID of the Scout APM application.
        endpoint_id (str | None): The ID of the endpoint to filter errors. If None,
                                  fetches all errors for the app.
        error_group_id (str | None): The ID of the error group to filter errors.
    """
    try:
        duration = scout_api.make_duration(from_, to)
        async with api_client as scout_client:
            if error_group_id:
                errors = await scout_client.get_error_group(app_id, error_group_id)
                errors = [errors] if errors else []
            else:
                errors = await scout_client.get_error_groups(
                    app_id, duration, endpoint_id
                )
        return errors
    except scout_api.ScoutAPMError as e:
        return [{"error": str(e)}]


@mcp.tool(name="get_app_insights")
async def get_app_insights(
    app_id: int, insight_type: str | None = None, limit: int | None = None
) -> dict[str, Any]:
    """
    Get or generate all insights for an application (cached for 5 minutes).

    Returns performance insights including N+1 queries, memory bloat, and slow queries.
    Each insight type includes count, new_count, and items array with specific details.
    If insight_type is provided, only that type will be returned.

    Args:
        app_id (int): The ID of the Scout APM application.
        insight_type: (str | None): Type of insight to filter (n_plus_one, memory_bloat,
                                    slow_query) If None (the default), all types will
                                    be returned.
        limit (int | None): Maximum number of items per insight type (default: 20).
    """
    try:
        async with api_client as scout_client:
            if insight_type is None:
                insights = await scout_client.get_insights(app_id, limit)
            else:
                insights = await scout_client.get_insight_by_type(
                    app_id, insight_type, limit
                )
        return insights
    except scout_api.ScoutAPMError as e:
        return {"error": str(e)}
