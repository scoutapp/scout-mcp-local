# Scout APM Setup for Dash

## Installation

Plotly Dash is built on top of Flask, so you should use the Scout Flask integration.

### Step 1: Install the scout-apm package

```bash
pip install scout-apm
```

### Step 2: Configure Scout with your Dash app

```python
import dash
from scout_apm.flask import ScoutApm

# Create Dash app
app = dash.Dash("myapp")
app.config.suppress_callback_exceptions = True

# Get the underlying Flask app
flask_app = app.server

# Setup Scout (as per Flask integration)
ScoutApm(flask_app)

# Configure Scout
flask_app.config["SCOUT_MONITOR"] = True
flask_app.config["SCOUT_KEY"] = "{SCOUT_KEY}"
flask_app.config["SCOUT_NAME"] = "{APP_NAME}"
```

**Alternative: Using Environment Variables**

Remove the `flask_app.config` Scout settings and set these environment variables:
- `SCOUT_MONITOR=true`
- `SCOUT_KEY={SCOUT_KEY}`
- `SCOUT_NAME={APP_NAME}`

### Step 3: Deploy

Deploy your application. It takes approximately five minutes for your data to first appear within the Scout UI.

## Heroku Customers

If you've installed Scout via the Heroku Addon, the provisioning process automatically sets `SCOUT_MONITOR` and `SCOUT_KEY` via config vars. Only `SCOUT_NAME` is additionally required.

## Documentation

For more information, visit: https://scoutapm.com/docs/python/other-libraries#dash

