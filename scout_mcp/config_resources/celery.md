# Scout APM Setup for Celery

## Installation

Scout supports Celery 4.0+.

### Step 1: Install the scout-apm package

```bash
pip install scout-apm
```

### Step 2: Configure Scout in your Celery app

```python
from celery import Celery
from scout_apm.api import Config
from scout_apm.celery import install

# Configure Scout
Config.set(
    key="{SCOUT_KEY}",
    name="{APP_NAME}",
    monitor=True,
)

# Create Celery app
app = Celery('tasks')

# Install Scout instrumentation
install(app)
```

**Alternative: Using Environment Variables**

Set these environment variables:
- `SCOUT_MONITOR=true`
- `SCOUT_KEY={SCOUT_KEY}`
- `SCOUT_NAME={APP_NAME}`

Then you don't need to call `Config.set()` - Scout will automatically use the environment variables.

### Step 3: Deploy

Deploy your application. It takes approximately five minutes for your data to first appear within the Scout UI.

Tasks will appear in the "Background Jobs" area of the Scout UI.

## Heroku Customers

If you've installed Scout via the Heroku Addon, the provisioning process automatically sets `SCOUT_MONITOR` and `SCOUT_KEY` via config vars. Only `SCOUT_NAME` is additionally required.

## Documentation

For more information, visit: https://scoutapm.com/docs/python/celery

