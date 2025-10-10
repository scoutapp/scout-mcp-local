# Scout APM Setup for Hug

## Installation

Scout supports Hug 2.4.0+.

### Step 1: Install the scout-apm package

```bash
pip install scout-apm
```

### Step 2: Configure Scout and add middleware

```python
import hug
from scout_apm.api import Config
from scout_apm.hug import ScoutMiddleware

# Configure Scout
Config.set(
    key="{SCOUT_KEY}",
    name="{APP_NAME}",
    monitor=True,
)

# Add Scout middleware to your Hug API
@hug.middleware_class()
class ScoutHugMiddleware(ScoutMiddleware):
    pass
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

For more information, visit: https://scoutapm.com/docs/python/other-libraries#hug

