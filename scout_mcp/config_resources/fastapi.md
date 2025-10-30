# Scout APM Setup for FastAPI

## Installation

Scout supports FastAPI through the Starlette instrumentation.

### Step 1: Install the scout-apm package

```bash
pip install scout-apm
```

### Step 2: Attach Scout middleware to your FastAPI app

Configure Scout and add the middleware to your FastAPI application:

```python
from fastapi import FastAPI
from scout_apm.api import Config
from scout_apm.async_.starlette import ScoutMiddleware

# Configure Scout
Config.set(
    key="{SCOUT_KEY}",
    name="{APP_NAME}",
    monitor=True,
    errors_enabled=True  # Recommended: Enable error tracking
)

# Create FastAPI app
app = FastAPI()

# Add Scout middleware
app.add_middleware(ScoutMiddleware)
```

**Alternative: Using Environment Variables**

Instead of hardcoding values in `Config.set()`, you can use environment variables:

Set these environment variables:
- `SCOUT_MONITOR=true`
- `SCOUT_KEY={SCOUT_KEY}`
- `SCOUT_NAME={APP_NAME}`

Then you don't need to call `Config.set()` - Scout will automatically use the environment variables.

### Step 3: Deploy

Deploy your application. It takes approximately five minutes for your data to first appear within the Scout UI.

## Heroku Customers

If you've installed Scout via the Heroku Addon, the provisioning process automatically sets `SCOUT_MONITOR` and `SCOUT_KEY` via config vars. Only `SCOUT_NAME` is additionally required.

## Complete Example

Here's a complete example of a FastAPI app with Scout configured:

```python
from fastapi import FastAPI
from scout_apm.api import Config
from scout_apm.async_.starlette import ScoutMiddleware
import os

# Configure Scout using environment variables (recommended for production)
Config.set(
    key=os.environ.get("SCOUT_KEY", "{SCOUT_KEY}"),
    name=os.environ.get("SCOUT_NAME", "{APP_NAME}"),
    monitor=os.environ.get("SCOUT_MONITOR", "True").lower() == "true",
)

# Create FastAPI app
app = FastAPI()

# Add Scout middleware
app.add_middleware(ScoutMiddleware)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Run with: uvicorn main:app --reload
```

## Important Notes

- Scout uses **Starlette** instrumentation for FastAPI
- The middleware should be added **after** creating your FastAPI app
- Scout works with both sync and async FastAPI endpoints
- Middleware will automatically track request/response times and errors

## Documentation

For more information, visit: https://scoutapm.com/docs/python/fastapi
