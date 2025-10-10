# Scout APM Setup for SQLAlchemy

## Installation

Scout can instrument standalone SQLAlchemy applications.

### Step 1: Install the scout-apm package

```bash
pip install scout-apm
```

### Step 2: Instrument your SQLAlchemy engine

```python
from sqlalchemy import create_engine
from scout_apm.sqlalchemy import instrument_sqlalchemy
from scout_apm.api import Config

# Configure Scout
Config.set(
    key="{SCOUT_KEY}",
    name="{APP_NAME}",
    monitor=True,
)

# Create your SQLAlchemy engine
engine = create_engine('postgresql://user:password@localhost/dbname')

# Instrument the engine with Scout
instrument_sqlalchemy(engine)
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

- For **Flask-SQLAlchemy**, use the Flask integration with `scout_apm.flask.sqlalchemy.instrument_sqlalchemy(db)`
- For **Django**, SQLAlchemy instrumentation is automatically applied when using Django ORM
- Scout automatically instruments common database drivers including PostgreSQL (psycopg2, asyncpg), MySQL (mysqlclient, PyMySQL), and SQLite

## Heroku Customers

If you've installed Scout via the Heroku Addon, the provisioning process automatically sets `SCOUT_MONITOR` and `SCOUT_KEY` via config vars. Only `SCOUT_NAME` is additionally required.

## Documentation

For more information, visit: https://scoutapm.com/docs/python/sqlalchemy

