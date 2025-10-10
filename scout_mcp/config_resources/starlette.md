# Scout APM Setup for Starlette

## Installation

Scout supports Starlette 0.12+.

### Step 1: Install the scout-apm package

```bash
pip install scout-apm
```

### Step 2: Configure Scout and attach middleware

```python
from scout_apm.api import Config
from scout_apm.async_.starlette import ScoutMiddleware
from starlette.applications import Starlette
from starlette.middleware import Middleware

# Configure Scout
Config.set(
    key="{SCOUT_KEY}",
    name="{APP_NAME}",
    monitor=True,
)

# Add Scout as the first middleware (outermost)
middleware = [
    Middleware(ScoutMiddleware),
]

app = Starlette(middleware=middleware)
```

**For Starlette < 0.13 (old middleware API):**

```python
app = Starlette()
app.add_middleware(ScoutMiddleware)  # Make this the last call to add_middleware
```

**Alternative: Using Environment Variables**

Set these environment variables:
- `SCOUT_MONITOR=true`
- `SCOUT_KEY={SCOUT_KEY}`
- `SCOUT_NAME={APP_NAME}`

Then you don't need to call `Config.set()` - Scout will automatically use the environment variables.

### Step 3: Deploy

Deploy your application. It takes approximately five minutes for your data to first appear within the Scout UI.

## Important Notes

- Scout middleware should be the **first** in your middleware stack (outermost) so it can track all requests
- For **FastAPI** applications, see the separate FastAPI configuration guide as it has specific setup requirements

## Heroku Customers

If you've installed Scout via the Heroku Addon, the provisioning process automatically sets `SCOUT_MONITOR` and `SCOUT_KEY` via config vars. Only `SCOUT_NAME` is additionally required.

## Documentation

For more information, visit: https://scoutapm.com/docs/python/other-libraries#starlette

