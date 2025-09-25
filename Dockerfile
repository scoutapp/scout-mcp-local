FROM python:3.13-slim

WORKDIR /app

# Install uv for faster dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY . .

# Install the package
RUN uv sync --frozen

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the MCP server using the main script
CMD ["uv", "run", "scout-mcp"]
