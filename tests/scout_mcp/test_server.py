from unittest.mock import AsyncMock, patch

import pytest

from scout_mcp import server
from scout_mcp import scout_api


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
            scout_api.ScoutAPMAsync, "get_jobs", new_callable=AsyncMock, return_value=mock_jobs
        ):
            result = await server.get_app_jobs(1, "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z")
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
            result = await server.get_app_jobs(1, "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z")
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
