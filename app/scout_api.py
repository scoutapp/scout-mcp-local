"""
Scout APM Python SDK

A simple Python SDK for the Scout APM API.
Supports all authentication methods and endpoints from the Scout APM API v0.

Usage:
    from scout_apm_sdk import ScoutAPMAsync
    import asyncio

    async def main():
        async with ScoutAPMAsync(api_key="your_api_key_here") as client:
            apps = await client.get_apps()

    asyncio.run(main())
"""

import dataclasses
import json
import logging
from abc import ABC
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

import httpx

log = logging.getLogger(__name__)

VALID_METRICS = {
    "response_time",
    "response_time_95th",
    "errors",
    "throughput",
    "queue_time",
    "apdex",
}


class ScoutAPMError(Exception):
    """Base exception for Scout APM SDK errors."""

    pass


class ScoutAPMAuthError(ScoutAPMError):
    """Raised when authentication fails."""

    pass


class ScoutAPMAPIError(ScoutAPMError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


@dataclasses.dataclass()
class Duration:
    start: datetime
    end: datetime


class ScoutAPMBase(ABC):
    """Base class for Scout APM clients with shared functionality."""

    BASE_URL = "https://scoutapm.com/api"
    API_VERSION = "v0"

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize Scout APM client base.

        Args:
            api_key: Your Scout APM API key
            base_url: Optional custom base URL (defaults to https://scoutapm.com/api)
                (default: "header")
        """
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL

    def _get_url(self, endpoint: str) -> str:
        """Construct full URL for an endpoint."""
        return f"{self.base_url}/{self.API_VERSION}/{endpoint.lstrip('/')}"

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return {"X-SCOUT-API": self.api_key}

    def _handle_response_errors(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle common response errors and parse JSON."""
        # Try to parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise ScoutAPMAPIError(
                f"Invalid JSON response: {response.text}", response.status_code
            )

        # Check for API-level errors
        if response.status_code == 401:
            raise ScoutAPMAuthError("Authentication failed - check your API key")

        if response.status_code >= 400:
            error_msg = "API request failed"
            if "header" in data and "status" in data["header"]:
                error_msg = data["header"]["status"].get("message", error_msg)
            raise ScoutAPMAPIError(error_msg, response.status_code, data)

        # Check for Scout APM specific error format
        if "header" in data and "status" in data["header"]:
            status_code = data["header"]["status"].get("code")
            if status_code and status_code >= 400:
                error_msg = data["header"]["status"].get("message", "Unknown API error")
                raise ScoutAPMAPIError(error_msg, status_code, data)

        return data

    def _validate_metric_params(self, metric_type: str, duration: Duration):
        """Validate metric parameters.

        Checks that metric_type is valid and that the time range does not
        exceed 2 weeks.
        """
        if metric_type not in VALID_METRICS:
            raise ValueError(
                f"Invalid metric_type. Must be one of: {', '.join(VALID_METRICS)}"
            )

        # Validate time range (2 week maximum)
        self._validate_time_range(duration)

    def _validate_time_range(self, duration: Duration):
        """Validate time ranges. Cannot exceed 2 weeks and from_time must be
        before to_time."""
        if duration.start >= duration.end:
            raise ValueError("from_time must be before to_time")
        if duration.end - duration.start > timedelta(days=14):
            raise ValueError("Time range cannot exceed 2 weeks")


class ScoutAPMAsync(ScoutAPMBase):
    """Asynchronous Scout APM API client."""

    def __init__(
        self,
        api_key: str = "",
        base_url: Optional[str] = None,
    ):
        """Initialize asynchronous Scout APM client."""
        super().__init__(api_key, base_url)
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    async def aclose(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            # TODO: Implement proper reuse.
            self.client = None

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Make an asynchronous API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: URL parameters
            json_data: JSON request body

        Returns:
            Dict containing the API response

        Raises:
            ScoutAPMAuthError: When authentication fails
            ScoutAPMAPIError: When the API returns an error
        """
        client = self.get_client()
        url = self._get_url(endpoint)
        log.debug(
            f"Making {method} request to {url} with params "
            f"{params} and data {json_data}"
        )

        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data if json_data else None,
            )

            return self._handle_response_errors(response)

        except httpx.RequestError as e:
            raise ScoutAPMAPIError(f"Network error: {str(e)}")

    def get_client(self) -> httpx.AsyncClient:
        """Get or initialize the HTTP client."""
        if not self.client:
            if not self.api_key:
                raise ValueError("API key is required")
            self.client = httpx.AsyncClient(
                headers=self._get_auth_headers(), timeout=30.0
            )
        return self.client

    async def get_apps(self) -> List[Dict[str, Union[int, str]]]:
        """Get list of all applications."""
        response = await self._make_request("GET", "apps")
        return response.get("results", {}).get("apps", [])

    async def get_app(self, app_id: int) -> Dict[str, Union[int, str]]:
        """Get details for a specific application."""
        response = await self._make_request("GET", f"apps/{app_id}")
        return response.get("results", {}).get("app", {})

    async def get_metrics(self, app_id: int) -> List[str]:
        """Get list of available metrics for an application."""
        response = await self._make_request("GET", f"apps/{app_id}/metrics")
        return response.get("results", {}).get("availableMetrics", [])

    async def get_metric_data(
        self, app_id: int, metric_type: str, duration: Duration
    ) -> Dict[str, List]:
        """Get time series data for a specific metric."""
        self._validate_metric_params(metric_type, duration)

        from_, to = (_format_time(duration.start), _format_time(duration.end))
        params = {"from": from_, "to": to}

        response = await self._make_request(
            "GET", f"apps/{app_id}/metrics/{metric_type}", params=params
        )
        return response.get("results", {}).get("series", {})

    async def get_endpoints(
        self, app_id: int, duration: Duration, full: bool = True
    ) -> List[Dict[str, str]]:
        """Get list of endpoints for an application."""
        self._validate_time_range(duration)
        params = {
            "full": full,
            "from": _format_time(duration.start),
            "to": _format_time(duration.end),
        }
        response = await self._make_request(
            "GET", f"apps/{app_id}/endpoints", params=params
        )
        return response.get("results", [])

    async def get_endpoint_metric(
        self,
        app_id: int,
        endpoint_id: str,
        metric: str,
        duration: Duration,
    ) -> List[str]:
        """Get metric data for a specific endpoint."""
        self._validate_metric_params(metric, duration)
        response = await self._make_request(
            "GET",
            f"apps/{app_id}/endpoints/{endpoint_id}/metrics/{metric}",
            params=self._get_duration_params(duration),
        )
        return response.get("results", {}).get("series", {}).get(metric, [])

    async def get_endpoint_traces(
        self,
        app_id: int,
        endpoint_id: str,
        duration: Duration,
    ) -> List[Dict[str, Any]]:
        """Get traces for a specific endpoint."""
        self._validate_time_range(duration)

        # Validate that from_time is not older than 7 days
        seven_days_ago = datetime.now(tz=timezone.utc) - timedelta(days=7)
        if duration.start < seven_days_ago:
            raise ValueError("from_time cannot be older than 7 days")

        response = await self._make_request(
            "GET",
            f"apps/{app_id}/endpoints/{endpoint_id}/traces",
            params=self._get_duration_params(duration),
        )
        return response.get("results", {}).get("traces", [])

    async def get_trace(self, app_id: int, trace_id: int) -> Dict[str, Any]:
        """Get a specific trace with all its spans."""
        response = await self._make_request(
            "GET",
            f"apps/{app_id}/traces/{trace_id}",
        )
        return response.get("results", {}).get("trace", {})

    async def get_error_groups(
        self, app_id: int, duration: Duration, endpoint: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get error problem groups for an application."""
        self._validate_time_range(duration)
        params = self._get_duration_params(duration)
        if endpoint:
            params["endpoint"] = endpoint

        response = await self._make_request(
            "GET",
            f"apps/{app_id}/error_groups",
            params=params,
        )
        return response.get("results", {}).get("error_groups", [])

    async def get_error_group(self, app_id: int, error_group_id: int) -> Dict[str, Any]:
        """Get a specific error problem group with its latest problem."""
        response = await self._make_request(
            "GET",
            f"apps/{app_id}/error_groups/{error_group_id}",
        )
        return response.get("results", {}).get("error_group", {})

    async def get_error_group_errors(
        self, app_id: int, error_group_id: int
    ) -> List[Dict[str, Any]]:
        """Get the most recent 100 problems for an error group."""
        response = await self._make_request(
            "GET",
            f"apps/{app_id}/error_groups/{error_group_id}/errors",
        )
        return response.get("results", {}).get("errors", [])

    async def get_app_summary(self, app_id: int) -> Dict[str, Any]:
        """Get a summary of application information."""
        app_details = await self.get_app(app_id)
        available_metrics = await self.get_metrics(app_id)

        return {"app": app_details, "available_metrics": available_metrics}

    def _get_duration_params(self, duration: Duration) -> Dict[str, str]:
        """Get duration parameters for API requests."""
        return {
            "from": _format_time(duration.start),
            "to": _format_time(duration.end),
        }

    async def get_insights(
        self, app_id: int, limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get all insights for an application (cached for 5 minutes)."""
        params = {}
        if limit is not None:
            params["limit"] = limit

        response = await self._make_request(
            "GET", f"apps/{app_id}/insights", params=params if params else None
        )
        return response.get("results", {})

    async def get_insight_by_type(
        self, app_id: int, insight_type: str, limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get data for a specific insight type.
        
        Args:
            app_id: Application ID
            insight_type: Type of insight (n_plus_one, memory_bloat, slow_query)
            limit: Maximum number of items (default: 20)
        """
        valid_types = {"n_plus_one", "memory_bloat", "slow_query"}
        if insight_type not in valid_types:
            raise ValueError(
                f"Invalid insight_type. Must be one of: {', '.join(valid_types)}"
            )

        params = {}
        if limit is not None:
            params["limit"] = limit

        response = await self._make_request(
            "GET", 
            f"apps/{app_id}/insights/{insight_type}", 
            params=params if params else None
        )
        return response.get("results", {})


def make_duration(from_: str, to: str) -> Duration:
    """Helper to create a Duration object from ISO 8601 strings."""
    start = _parse_time(from_)
    end = _parse_time(to)
    return Duration(start=start, end=end)


def get_endpoint_id(endpoint: dict[str, Any]) -> str:
    """
    Helper to get a unique identifier for an endpoint.
    This is provided by the API implicitly in the 'link' field.
    Args:
        endpoint: Endpoint dictionary from the API.
    """
    link = endpoint.get("link", "")
    return link.split("/")[-1] if link else ""


def _format_time(dt: datetime) -> str:
    """Format datetime to ISO 8601 string for API. Relies on UTC timezone."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_time(time_str: str) -> datetime:
    """Parse ISO 8601 time string to datetime object."""
    return datetime.fromisoformat(time_str.replace("Z", "+00:00")).astimezone(
        timezone.utc
    )
