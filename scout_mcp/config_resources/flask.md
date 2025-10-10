# Scout APM Setup for Flask

## Installation

### Step 1: Install the scout-apm package

```bash
pip install scout-apm
```

### Step 2: Configure Scout inside your Flask app

Import and attach ScoutApm to your Flask application:

```python
from flask import Flask
from scout_apm.flask import ScoutApm

# Setup a Flask app as normal
app = Flask(__name__)

# Attach ScoutApm to the Flask App
ScoutApm(app)

# Scout settings
app.config["SCOUT_MONITOR"] = True
app.config["SCOUT_KEY"] = "{SCOUT_KEY}"
app.config["SCOUT_NAME"] = "{APP_NAME}"
```

**Alternative: Using Environment Variables**

Instead of hardcoding values in your app configuration, you can use environment variables:

Remove the `app.config` Scout settings and set these environment variables:
- `SCOUT_MONITOR=true`
- `SCOUT_KEY={SCOUT_KEY}`
- `SCOUT_NAME={APP_NAME}`

Then Scout will automatically pick them up.

### Step 3: Flask SQLAlchemy (Optional)

If you're using Flask-SQLAlchemy, you can instrument database queries:

```python
from flask_sqlalchemy import SQLAlchemy
from scout_apm.flask.sqlalchemy import instrument_sqlalchemy

app = Flask(__name__)
db = SQLAlchemy(app)
instrument_sqlalchemy(db)
```

### Step 4: Deploy

Deploy your application. It takes approximately five minutes for your data to first appear within the Scout UI.

## Heroku Customers

If you've installed Scout via the Heroku Addon, the provisioning process automatically sets `SCOUT_MONITOR` and `SCOUT_KEY` via config vars. Only `SCOUT_NAME` is additionally required.

## Complete Example

Here's a complete example of a Flask app with Scout configured:

```python
from flask import Flask
from scout_apm.flask import ScoutApm
import os

app = Flask(__name__)

# Attach Scout
ScoutApm(app)

# Configure Scout (using environment variables is recommended for production)
app.config["SCOUT_MONITOR"] = os.environ.get("SCOUT_MONITOR", "True").lower() == "true"
app.config["SCOUT_KEY"] = os.environ.get("SCOUT_KEY", "{SCOUT_KEY}")
app.config["SCOUT_NAME"] = os.environ.get("SCOUT_NAME", "{APP_NAME}")

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()
```

## Documentation

For more information, visit: https://scoutapm.com/docs/python/flask
