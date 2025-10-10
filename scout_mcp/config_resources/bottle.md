# Scout APM Setup for Bottle

## Installation

### Step 1: Install the scout-apm package

```bash
pip install scout-apm
```

### Step 2: Add Scout to your Bottle config

```python
from scout_apm.bottle import ScoutPlugin
import bottle

app = bottle.default_app()
app.config.update({
    "scout.name": "{APP_NAME}",
    "scout.key": "{SCOUT_KEY}",
    "scout.monitor": True,
})

scout = ScoutPlugin()
bottle.install(scout)
```

**Alternative: Using Environment Variables**

Remove the `app.config.update` call and set these environment variables:
- `SCOUT_MONITOR=true`
- `SCOUT_KEY={SCOUT_KEY}`
- `SCOUT_NAME={APP_NAME}`

### Step 3: Deploy

Deploy your application. It takes approximately five minutes for your data to first appear within the Scout UI.

## Heroku Customers

If you've installed Scout via the Heroku Addon, the provisioning process automatically sets `SCOUT_MONITOR` and `SCOUT_KEY` via config vars. Only `SCOUT_NAME` is additionally required.

## Documentation

For more information, visit: https://scoutapm.com/docs/python/other-libraries#bottle

