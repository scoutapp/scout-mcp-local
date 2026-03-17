from unittest.mock import AsyncMock, patch

import pytest

from scout_mcp import scout_api, server
from scout_mcp.scout_api import ScoutAPMAuthError


def test_server():
    assert server.mcp


class TestGetAppJobs:
    @pytest.mark.asyncio
    async def test_get_app_jobs_success(self):
        mock_jobs = [
            {
                "full_name": "EmailJob",
                "name": "EmailJob",
                "queue": "default",
                "job_id": "RW1haWxKb2I=",
                "throughput": 100,
                "execution_time": 250,
                "time_consumed": 25000,
                "latency": 50,
            },
        ]

        with patch.object(
            scout_api.ScoutAPMAsync,
            "get_jobs",
            new_callable=AsyncMock,
            return_value=mock_jobs,
        ):
            result = await server.get_app_jobs(
                1, "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"
            )
            assert len(result) == 1
            assert result[0]["full_name"] == "EmailJob"

    @pytest.mark.asyncio
    async def test_get_app_jobs_error(self):
        with patch.object(
            scout_api.ScoutAPMAsync,
            "get_jobs",
            new_callable=AsyncMock,
            side_effect=scout_api.ScoutAPMAPIError("API error"),
        ):
            result = await server.get_app_jobs(
                1, "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"
            )
            assert result[0]["error"] == "API error"


class TestGetJobMetrics:
    @pytest.mark.asyncio
    async def test_get_job_metric_success(self):
        mock_data = [[1704067200, 250], [1704070800, 300]]

        with patch.object(
            scout_api.ScoutAPMAsync,
            "get_job_metric",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await server.get_job_metric(
                1, "RW1haWxKb2I=", "execution_time",
                "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z",
            )
            assert result["metric"] == "execution_time"
            assert result["data_points"] == 2
            assert result["series"] == mock_data

    @pytest.mark.asyncio
    async def test_get_job_metric_invalid_metric(self):
        result = await server.get_job_metric(
            1, "RW1haWxKb2I=", "apdex",
            "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z",
        )
        assert "error" in result
        assert "Invalid metric" in result["error"]

    @pytest.mark.asyncio
    async def test_get_job_metric_no_data(self):
        with patch.object(
            scout_api.ScoutAPMAsync,
            "get_job_metric",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await server.get_job_metric(
                1, "RW1haWxKb2I=", "execution_time",
                "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z",
            )
            assert "error" in result
            assert "No data available" in result["error"]


class TestGetAppJobTraces:
    @pytest.mark.asyncio
    async def test_get_app_job_traces_success(self):
        mock_traces = [
            {
                "id": 1,
                "time": "2024-01-07T10:00:00Z",
                "duration": 500,
                "name": "EmailJob",
                "queue": "default",
                "metric_name": "Job/EmailJob",
                "context": {},
            }
        ]

        with patch.object(
            scout_api.ScoutAPMAsync,
            "get_job_traces",
            new_callable=AsyncMock,
            return_value=mock_traces,
        ):
            result = await server.get_app_job_traces(
                1, "2024-01-07T00:00:00Z", "2024-01-07T12:00:00Z", "RW1haWxKb2I=",
            )
            assert len(result) == 1
            assert result[0]["name"] == "EmailJob"

    @pytest.mark.asyncio
    async def test_get_app_job_traces_error(self):
        with patch.object(
            scout_api.ScoutAPMAsync,
            "get_job_traces",
            new_callable=AsyncMock,
            side_effect=scout_api.ScoutAPMAPIError("API error"),
        ):
            result = await server.get_app_job_traces(
                1, "2024-01-07T00:00:00Z", "2024-01-07T12:00:00Z", "RW1haWxKb2I=",
            )
            assert result[0]["error"] == "API error"


class TestGetUsageTool:
    """Tests for the get_usage MCP tool."""

    @pytest.mark.asyncio
    async def test_basic_per_transaction(self):
        usage_data = {
            "billing_period": {"start": "2024-01-01T00:00:00Z", "end": "2024-02-01T00:00:00Z"},
            "pricing_style": "per transaction",
            "apm": {"total_transactions": 500000},
        }
        with patch.object(server.api_client, "get_usage", new=AsyncMock(return_value=usage_data)):
            result = await server.get_usage()

        assert "2024-01-01T00:00:00Z" in result
        assert "per transaction" in result
        assert "500,000" in result
        assert "unlimited" in result

    @pytest.mark.asyncio
    async def test_apm_with_limit(self):
        usage_data = {
            "billing_period": {"start": "2024-01-01T00:00:00Z", "end": "2024-02-01T00:00:00Z"},
            "pricing_style": "per transaction",
            "apm": {"total_transactions": 500000, "limit": 1000000},
        }
        with patch.object(server.api_client, "get_usage", new=AsyncMock(return_value=usage_data)):
            result = await server.get_usage()

        assert "500,000 / 1,000,000" in result

    @pytest.mark.asyncio
    async def test_per_node_pricing_shows_nodes(self):
        usage_data = {
            "billing_period": {"start": "2024-01-01T00:00:00Z", "end": "2024-02-01T00:00:00Z"},
            "pricing_style": "per node",
            "apm": {"total_transactions": 200000},
            "nodes": {"active_count": 5},
        }
        with patch.object(server.api_client, "get_usage", new=AsyncMock(return_value=usage_data)):
            result = await server.get_usage()

        assert "Active nodes: 5" in result

    @pytest.mark.asyncio
    async def test_errors_section_when_present(self):
        usage_data = {
            "billing_period": {"start": "2024-01-01T00:00:00Z", "end": "2024-02-01T00:00:00Z"},
            "pricing_style": "per transaction",
            "apm": {"total_transactions": 100000},
            "errors": {"count": 150, "limit": 1000},
        }
        with patch.object(server.api_client, "get_usage", new=AsyncMock(return_value=usage_data)):
            result = await server.get_usage()

        assert "150 / 1,000" in result

    @pytest.mark.asyncio
    async def test_errors_section_absent_when_not_present(self):
        usage_data = {
            "billing_period": {"start": "2024-01-01T00:00:00Z", "end": "2024-02-01T00:00:00Z"},
            "pricing_style": "per transaction",
            "apm": {"total_transactions": 100000},
        }
        with patch.object(server.api_client, "get_usage", new=AsyncMock(return_value=usage_data)):
            result = await server.get_usage()

        assert "Errors" not in result

    @pytest.mark.asyncio
    async def test_logs_section_when_present(self):
        usage_data = {
            "billing_period": {"start": "2024-01-01T00:00:00Z", "end": "2024-02-01T00:00:00Z"},
            "pricing_style": "per transaction",
            "apm": {"total_transactions": 100000},
            "logs": {"bytes_used": 1073741824, "limit_bytes": 10737418240},
        }
        with patch.object(server.api_client, "get_usage", new=AsyncMock(return_value=usage_data)):
            result = await server.get_usage()

        assert "1.00 GB / 10.00 GB" in result

    @pytest.mark.asyncio
    async def test_api_error_returns_error_string(self):
        with patch.object(
            server.api_client,
            "get_usage",
            new=AsyncMock(side_effect=ScoutAPMAuthError("Authentication failed")),
        ):
            result = await server.get_usage()

        assert "Error:" in result
        assert "Authentication failed" in result
