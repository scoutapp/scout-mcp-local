# Scout APM Setup for Falcon

## Installation

Scout supports Falcon 2.0+.

### Step 1: Install the scout-apm package

```bash
pip install scout-apm
```

### Step 2: Configure Scout and add middleware

```python
import falcon
from scout_apm.api import Config
from scout_apm.falcon import ScoutMiddleware

# Configure Scout
Config.set(
    key="{SCOUT_KEY}",
    name="{APP_NAME}",
    monitor=True,
)

# Create Falcon app with Scout middleware
app = falcon.App(middleware=[ScoutMiddleware()])
```

**For Falcon 2.x (using the old API class):**

```python
app = falcon.API(middleware=[ScoutMiddleware()])
```

**Alternative: Using Environment Variables**

Set these environment variables:
- `SCOUT_MONITOR=true`
- `SCOUT_KEY={SCOUT_KEY}`
- `SCOUT_NAME={APP_NAME}`

Then you don't need to call `Config.set()` - Scout will automatically use the environment variables.

### Step 3: Deploy

Deploy your application. It takes approximately five minutes for your data to first appear within the Scout UI.

## Heroku Customers

If you've installed Scout via the Heroku Addon, the provisioning process automatically sets `SCOUT_MONITOR` and `SCOUT_KEY` via config vars. Only `SCOUT_NAME` is additionally required.

## Documentation

For more information, visit: https://scoutapm.com/docs/python/other-libraries#falcon

