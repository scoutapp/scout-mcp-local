"""
Comprehensive test suite for Scout APM Python SDK

This has been auto-generated and will be manually reviewed and edited.
"""

import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import httpx
import pytest

from scout_mcp.scout_api import (
    Duration,
    ScoutAPMAPIError,
    ScoutAPMAsync,
    ScoutAPMAuthError,
    ScoutAPMError,
    make_duration,
)


class TestScoutAPMBase:
    """Test base functionality shared by all Scout APM clients."""

    def test_init_default_values(self):
        """Test initialization with default values."""
        client = ScoutAPMAsync("test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://scoutapm.com/api"

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        client = ScoutAPMAsync("test_key", base_url="https://custom.url")
        assert client.api_key == "test_key"
        assert client.base_url == "https://custom.url"

    def test_get_url(self):
        """Test URL construction."""
        client = ScoutAPMAsync("test_key")
        assert client._get_url("apps") == "https://scoutapm.com/api/v0/apps"
        assert client._get_url("/apps") == "https://scoutapm.com/api/v0/apps"
        assert (
            client._get_url("apps/123/metrics")
            == "https://scoutapm.com/api/v0/apps/123/metrics"
        )

    def test_get_auth_headers_header_method(self):
        """Test auth headers for header method."""
        client = ScoutAPMAsync("test_key")
        headers = client._get_auth_headers()
        assert headers == {"X-SCOUT-API": "test_key"}

    def test_validate_metric_params_valid(self):
        """Test metric parameter validation with valid inputs."""
        client = ScoutAPMAsync("test_key")
        duration = make_duration("2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z")
        # Should not raise
        client._validate_metric_params("response_time", duration)

    def test_validate_metric_params_invalid_metric(self):
        """Test metric parameter validation with invalid metric."""
        client = ScoutAPMAsync("test_key")
        duration = make_duration("2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z")
        with pytest.raises(ValueError, match="Invalid metric_type"):
            client._validate_metric_params("invalid_metric", duration)

    def test_validate_time_range_valid(self):
        """Test time range validation with valid range."""
        client = ScoutAPMAsync("test_key")
        duration = Duration(
            start=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end=datetime(2024, 1, 2, tzinfo=timezone.utc),
        )
        # Should not raise
        client._validate_time_range(duration)

    def test_validate_time_range_start_after_end(self):
        """Test time range validation with start after end."""
        client = ScoutAPMAsync("test_key")
        duration = Duration(
            start=datetime(2024, 1, 2, tzinfo=timezone.utc),
            end=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        with pytest.raises(ValueError, match="from_time must be before to_time"):
            client._validate_time_range(duration)

    def test_validate_time_range_too_long(self):
        """Test time range validation with range too long."""
        client = ScoutAPMAsync("test_key")
        duration = Duration(
            start=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end=datetime(2024, 1, 16, tzinfo=timezone.utc),  # 15 days
        )
        with pytest.raises(ValueError, match="Time range cannot exceed 2 weeks"):
            client._validate_time_range(duration)

    def test_format_time(self):
        """Test time formatting."""
        from scout_mcp.scout_api import _format_time

        dt = datetime(2024, 1, 1, 12, 30, 45, tzinfo=timezone.utc)
        formatted = _format_time(dt)
        assert formatted == "2024-01-01T12:30:45Z"

    def test_parse_time(self):
        """Test time parsing."""
        from scout_mcp.scout_api import _parse_time

        parsed = _parse_time("2024-01-01T12:30:45Z")
        expected = datetime(2024, 1, 1, 12, 30, 45, tzinfo=timezone.utc)
        assert parsed == expected

    def test_handle_response_errors_success(self):
        """Test response error handling with successful response."""
        client = ScoutAPMAsync("test_key")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}

        result = client._handle_response_errors(mock_response)
        assert result == {"data": "success"}

    def test_handle_response_errors_invalid_json(self):
        """Test response error handling with invalid JSON."""
        client = ScoutAPMAsync("test_key")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "invalid json"

        with pytest.raises(ScoutAPMAPIError, match="Invalid JSON response"):
            client._handle_response_errors(mock_response)

    def test_handle_response_errors_401_auth_error(self):
        """Test response error handling with 401 auth error."""
        client = ScoutAPMAsync("test_key")
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}

        with pytest.raises(ScoutAPMAuthError, match="Authentication failed"):
            client._handle_response_errors(mock_response)

    def test_handle_response_errors_400_with_message(self):
        """Test response error handling with 400 and message."""
        client = ScoutAPMAsync("test_key")
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "header": {"status": {"message": "Bad request"}}
        }

        with pytest.raises(ScoutAPMAPIError, match="Bad request"):
            client._handle_response_errors(mock_response)

    def test_handle_response_errors_scout_error_format(self):
        """Test response error handling with Scout-specific error format."""
        client = ScoutAPMAsync("test_key")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "header": {"status": {"code": 404, "message": "Not found"}}
        }

        with pytest.raises(ScoutAPMAPIError, match="Not found"):
            client._handle_response_errors(mock_response)


class TestScoutAPMAsync:
    """Test asynchronous Scout APM client."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return ScoutAPMAsync("test_key")

    @pytest.fixture
    def mock_response_success(self):
        """Create a mock successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": {"apps": [{"id": 1, "name": "Test App"}]}
        }
        return mock_response

    @pytest.mark.asyncio
    async def test_aclose(self):
        """Test manual close."""
        client = ScoutAPMAsync("test_key")
        c = client.get_client()
        with patch.object(c, "aclose") as mock_close:
            await client.aclose()
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_success(self, client, mock_response_success):
        """Test successful API request."""
        c = client.get_client()
        with patch.object(
            c, "request", return_value=mock_response_success
        ) as mock_request:
            result = await client._make_request("GET", "apps")

            mock_request.assert_called_once_with(
                method="GET",
                url="https://scoutapm.com/api/v0/apps",
                params=None,
                json=None,
            )
            assert result == {"results": {"apps": [{"id": 1, "name": "Test App"}]}}

    @pytest.mark.asyncio
    async def test_make_request_network_error(self, client):
        """Test API request with network error."""
        c = client.get_client()  # Ensure client is initialized
        with patch.object(
            c, "request", side_effect=httpx.RequestError("Network error")
        ):
            with pytest.raises(ScoutAPMAPIError, match="Network error"):
                await client._make_request("GET", "apps")

    @pytest.mark.asyncio
    async def test_get_apps(self, client):
        """Test get_apps method."""
        mock_response = {
            "results": {
                "apps": [{"id": 1, "name": "App 1"}, {"id": 2, "name": "App 2"}]
            }
        }

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            apps = await client.get_apps()

            mock_request.assert_called_once_with("GET", "apps")
            assert apps == [{"id": 1, "name": "App 1"}, {"id": 2, "name": "App 2"}]

    @pytest.mark.asyncio
    async def test_get_apps_empty_results(self, client):
        """Test get_apps with empty results."""
        mock_response = {"results": {}}

        with patch.object(client, "_make_request", return_value=mock_response):
            apps = await client.get_apps()
            assert apps == []

    @pytest.mark.asyncio
    async def test_get_app(self, client):
        """Test get_app method."""
        mock_response = {"results": {"app": {"id": 1, "name": "Test App"}}}

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            app = await client.get_app(1)

            mock_request.assert_called_once_with("GET", "apps/1")
            assert app == {"id": 1, "name": "Test App"}

    @pytest.mark.asyncio
    async def test_get_metrics(self, client):
        """Test get_metrics method."""
        mock_response = {
            "results": {"availableMetrics": ["response_time", "throughput"]}
        }

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            metrics = await client.get_metrics(1)

            mock_request.assert_called_once_with("GET", "apps/1/metrics")
            assert metrics == ["response_time", "throughput"]

    @pytest.mark.asyncio
    async def test_get_metric_data(self, client):
        """Test get_metric_data method."""
        mock_response = {"results": {"series": {"response_time": [1.0, 2.0, 3.0]}}}
        duration = make_duration("2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z")

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            data = await client.get_metric_data(1, "response_time", duration)

            mock_request.assert_called_once_with(
                "GET",
                "apps/1/metrics/response_time",
                params={"from": "2024-01-01T00:00:00Z", "to": "2024-01-02T00:00:00Z"},
            )
            assert data == {"response_time": [1.0, 2.0, 3.0]}

    @pytest.mark.asyncio
    async def test_get_endpoints(self, client):
        """Test get_endpoints method."""
        mock_response = {
            "results": [
                {"id": "endpoint1", "name": "GET /users"},
                {"id": "endpoint2", "name": "POST /users"},
            ]
        }
        duration = make_duration("2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z")

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            endpoints = await client.get_endpoints(1, duration)

            assert len(mock_request.call_args_list) == 1
            assert endpoints == [
                {"id": "endpoint1", "name": "GET /users"},
                {"id": "endpoint2", "name": "POST /users"},
            ]

    @pytest.mark.asyncio
    async def test_get_endpoint_metric(self, client):
        """Test get_endpoint_metric method."""
        mock_response = {"results": {"series": {"response_time": [1.0, 2.0, 3.0]}}}
        duration = make_duration("2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z")

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            data = await client.get_endpoint_metric(
                1,
                "endpoint1",
                "response_time",
                duration,
            )

            mock_request.assert_called_once_with(
                "GET",
                "apps/1/endpoints/endpoint1/metrics/response_time",
                params={"from": "2024-01-01T00:00:00Z", "to": "2024-01-02T00:00:00Z"},
            )
            assert data == [1.0, 2.0, 3.0]

    @pytest.mark.asyncio
    async def test_get_endpoint_traces(self, client):
        """Test get_endpoint_traces method."""
        mock_response = {"results": {"traces": [{"id": 1, "duration": 100}]}}
        duration = make_duration("2024-01-07T00:00:00Z", "2024-01-07T12:00:00Z")

        # Mock datetime.now to return a fixed time for testing
        fixed_now = datetime(2024, 1, 8, tzinfo=timezone.utc)
        with patch("scout_mcp.scout_api.datetime") as mock_datetime:
            # Configure the mock to behave like the real datetime module
            mock_datetime.now.return_value = fixed_now
            mock_datetime.fromisoformat = datetime.fromisoformat
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            with patch.object(
                client, "_make_request", return_value=mock_response
            ) as mock_request:
                traces = await client.get_endpoint_traces(1, "endpoint1", duration)

                mock_request.assert_called_once_with(
                    "GET",
                    "apps/1/endpoints/endpoint1/traces",
                    params={
                        "from": "2024-01-07T00:00:00Z",
                        "to": "2024-01-07T12:00:00Z",
                    },
                )
                assert traces == [{"id": 1, "duration": 100}]

    @pytest.mark.asyncio
    async def test_get_endpoint_traces_too_old(self, client):
        """Test get_endpoint_traces with date too old."""
        duration = make_duration("2023-12-31T00:00:00Z", "2024-01-01T00:00:00Z")
        fixed_now = datetime(2024, 1, 8, tzinfo=timezone.utc)
        with patch("scout_mcp.scout_api.datetime") as mock_datetime:
            # Configure the mock to behave like the real datetime module
            mock_datetime.now.return_value = fixed_now
            mock_datetime.fromisoformat = datetime.fromisoformat
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            with pytest.raises(
                ValueError, match="from_time cannot be older than 7 days"
            ):
                await client.get_endpoint_traces(1, "endpoint1", duration)

    @pytest.mark.asyncio
    async def test_get_trace(self, client):
        """Test get_trace method."""
        mock_response = {"results": {"trace": {"id": 1, "spans": []}}}

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            trace = await client.get_trace(1, 123)

            mock_request.assert_called_once_with("GET", "apps/1/traces/123")
            assert trace == {"id": 1, "spans": []}

    @pytest.mark.asyncio
    async def test_get_error_groupss(self, client):
        """Test get_errors method."""
        mock_response = {"results": {"error_groups": [{"id": 1, "message": "Error"}]}}
        duration = make_duration("2024-01-07T00:00:00Z", "2024-01-07T12:00:00Z")

        fixed_now = datetime(2024, 1, 8, tzinfo=timezone.utc)
        with patch("scout_mcp.scout_api.datetime") as mock_datetime:
            # Configure the mock to behave like the real datetime module
            mock_datetime.now.return_value = fixed_now
            mock_datetime.fromisoformat = datetime.fromisoformat
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            with patch.object(
                client, "_make_request", return_value=mock_response
            ) as mock_request:
                errors = await client.get_error_groups(1, duration)

                mock_request.assert_called_once_with(
                    "GET",
                    "apps/1/error_groups",
                    params={
                        "from": "2024-01-07T00:00:00Z",
                        "to": "2024-01-07T12:00:00Z",
                    },
                )
                assert errors == [{"id": 1, "message": "Error"}]

    @pytest.mark.asyncio
    async def test_get_error_groups_with_endpoint(self, client):
        """Test get_errors method with endpoint filter."""
        mock_response = {"results": {"error_groups": []}}
        duration = make_duration("2024-01-07T00:00:00Z", "2024-01-07T12:00:00Z")

        fixed_now = datetime(2024, 1, 8, tzinfo=timezone.utc)
        with patch("scout_mcp.scout_api.datetime") as mock_datetime:
            # Configure the mock to behave like the real datetime module
            mock_datetime.now.return_value = fixed_now
            mock_datetime.fromisoformat = datetime.fromisoformat
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            with patch.object(
                client, "_make_request", return_value=mock_response
            ) as mock_request:
                res = await client.get_error_groups(
                    1,
                    duration,
                    endpoint="GET /users",
                )
                assert res == []

                mock_request.assert_called_once_with(
                    "GET",
                    "apps/1/error_groups",
                    params={
                        "from": "2024-01-07T00:00:00Z",
                        "to": "2024-01-07T12:00:00Z",
                        "endpoint": "GET /users",
                    },
                )

    @pytest.mark.asyncio
    async def test_get_error_group(self, client):
        """Test get_error method."""
        mock_response = {
            "results": {"error_group": {"id": 1, "message": "Error details"}}
        }

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            error = await client.get_error_group(1, 123)

            mock_request.assert_called_once_with("GET", "apps/1/error_groups/123")
            assert error == {"id": 1, "message": "Error details"}

    @pytest.mark.asyncio
    async def test_get_error_group_errors(self, client):
        """Test get_error_problems method."""
        mock_response = {
            "results": {"errors": [{"id": 1, "occurred_at": "2024-01-01"}]}
        }

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            problems = await client.get_error_group_errors(1, 123)

            mock_request.assert_called_once_with(
                "GET", "apps/1/error_groups/123/errors"
            )
            assert problems == [{"id": 1, "occurred_at": "2024-01-01"}]

    @pytest.mark.asyncio
    async def test_get_insights(self, client):
        """Test get_insights method."""
        mock_response = {
            "results": {
                "timeframe": {
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-02T00:00:00Z",
                    "duration_minutes": 1440,
                },
                "insights": {
                    "n_plus_one": {"count": 5, "new_count": 2, "items": []},
                    "memory_bloat": {"count": 3, "new_count": 1, "items": []},
                    "slow_query": {"count": 8, "new_count": 4, "items": []},
                },
            }
        }

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            insights = await client.get_insights(1)

            mock_request.assert_called_once_with("GET", "apps/1/insights", params=None)
            assert insights == mock_response["results"]

    @pytest.mark.asyncio
    async def test_get_insights_with_limit(self, client):
        """Test get_insights method with limit parameter."""
        mock_response = {
            "results": {
                "timeframe": {
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-02T00:00:00Z",
                    "duration_minutes": 1440,
                },
                "insights": {
                    "n_plus_one": {"count": 5, "new_count": 2, "items": []},
                    "memory_bloat": {"count": 3, "new_count": 1, "items": []},
                    "slow_query": {"count": 8, "new_count": 4, "items": []},
                },
            }
        }

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            insights = await client.get_insights(1, limit=10)

            mock_request.assert_called_once_with(
                "GET", "apps/1/insights", params={"limit": 10}
            )
            assert insights == mock_response["results"]

    @pytest.mark.asyncio
    async def test_get_insight_by_type_n_plus_one(self, client):
        """Test get_insight_by_type method with n_plus_one type."""
        mock_response = {
            "results": {
                "timeframe": {
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-02T00:00:00Z",
                    "duration_minutes": 1440,
                },
                "total_count": 5,
                "insight_type": "n_plus_one",
                "new_count": 2,
                "items": [
                    {"id": 1, "name": "User.posts query", "count": 15},
                    {"id": 2, "name": "Post.comments query", "count": 8},
                ],
            }
        }

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            insights = await client.get_insight_by_type(1, "n_plus_one")

            mock_request.assert_called_once_with(
                "GET", "apps/1/insights/n_plus_one", params=None
            )
            assert insights == mock_response["results"]

    @pytest.mark.asyncio
    async def test_get_insight_by_type_memory_bloat(self, client):
        """Test get_insight_by_type method with memory_bloat type."""
        mock_response = {
            "results": {
                "timeframe": {
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-02T00:00:00Z",
                    "duration_minutes": 1440,
                },
                "total_count": 3,
                "insight_type": "memory_bloat",
                "new_count": 1,
                "items": [
                    {
                        "id": 1,
                        "endpoint": "UsersController#show",
                        "allocations": 1000000,
                    }
                ],
            }
        }

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            insights = await client.get_insight_by_type(1, "memory_bloat")

            mock_request.assert_called_once_with(
                "GET", "apps/1/insights/memory_bloat", params=None
            )
            assert insights == mock_response["results"]

    @pytest.mark.asyncio
    async def test_get_insight_by_type_slow_query(self, client):
        """Test get_insight_by_type method with slow_query type."""
        mock_response = {
            "results": {
                "timeframe": {
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-02T00:00:00Z",
                    "duration_minutes": 1440,
                },
                "total_count": 8,
                "insight_type": "slow_query",
                "new_count": 4,
                "items": [
                    {"id": 1, "query": "SELECT * FROM users WHERE...", "duration": 2.5},
                    {"id": 2, "query": "SELECT * FROM posts WHERE...", "duration": 3.2},
                ],
            }
        }

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            insights = await client.get_insight_by_type(1, "slow_query")

            mock_request.assert_called_once_with(
                "GET", "apps/1/insights/slow_query", params=None
            )
            assert insights == mock_response["results"]

    @pytest.mark.asyncio
    async def test_get_insight_by_type_with_limit(self, client):
        """Test get_insight_by_type method with limit parameter."""
        mock_response = {
            "results": {
                "timeframe": {
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-02T00:00:00Z",
                    "duration_minutes": 1440,
                },
                "total_count": 5,
                "insight_type": "n_plus_one",
                "new_count": 2,
                "items": [{"id": 1, "name": "User.posts query", "count": 15}],
            }
        }

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            insights = await client.get_insight_by_type(1, "n_plus_one", limit=5)

            mock_request.assert_called_once_with(
                "GET", "apps/1/insights/n_plus_one", params={"limit": 5}
            )
            assert insights == mock_response["results"]

    @pytest.mark.asyncio
    async def test_get_insight_by_type_invalid_type(self, client):
        """Test get_insight_by_type method with invalid type."""
        with pytest.raises(ValueError, match="Invalid insight_type"):
            await client.get_insight_by_type(1, "invalid_type")


class TestExceptions:
    """Test custom exceptions."""

    def test_scout_apm_error(self):
        """Test base ScoutAPMError."""
        error = ScoutAPMError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_scout_apm_auth_error(self):
        """Test ScoutAPMAuthError inheritance."""
        error = ScoutAPMAuthError("Auth error")
        assert str(error) == "Auth error"
        assert isinstance(error, ScoutAPMError)

    def test_scout_apm_api_error_basic(self):
        """Test basic ScoutAPMAPIError."""
        error = ScoutAPMAPIError("API error")
        assert str(error) == "API error"
        assert error.status_code is None
        assert error.response_data is None

    def test_scout_apm_api_error_full(self):
        """Test ScoutAPMAPIError with all parameters."""
        response_data = {"error": "details"}
        error = ScoutAPMAPIError("API error", 400, response_data)
        assert str(error) == "API error"
        assert error.status_code == 400
        assert error.response_data == response_data
