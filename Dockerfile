FROM python:3.13-slim

WORKDIR /app

# Install uv for faster dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy source code
COPY server.py ./

# Expose port if desired for local testing
# EXPOSE 8999

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the MCP server
CMD ["uv", "run", "python", "server.py"]
