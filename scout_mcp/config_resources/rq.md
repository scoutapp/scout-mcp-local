# Scout APM Setup for RQ (Redis Queue)

## Installation

Scout supports RQ 1.0+.

### Step 1: Install the scout-apm package

```bash
pip install scout-apm
```

### Step 2: Use the Scout RQ worker class

**If using RQ directly:**

Pass the `--worker-class` argument to the worker command:

```bash
rq worker --worker-class scout_apm.rq.Worker myqueue
```

**If using RQ Heroku pattern:**

Change your code to use the Scout worker class:

```python
from scout_apm.rq import HerokuWorker as Worker
```

**If using Django-RQ:**

Use the custom worker setting:

```python
RQ = {
    "WORKER_CLASS": "scout_apm.rq.Worker",
}
```

### Step 3: Configure Scout

**If using RQ directly**, create a config file:

```python
from scout_apm.api import Config
  
Config.set(
    key="{SCOUT_KEY}",
    name="{APP_NAME}",
    monitor=True,
)
```

Pass the config file with `-c` argument to the worker command.

**Alternative: Using Environment Variables**

Set these environment variables:
- `SCOUT_MONITOR=true`
- `SCOUT_KEY={SCOUT_KEY}`
- `SCOUT_NAME={APP_NAME}`

### Step 4: Deploy

Deploy your application. It takes approximately five minutes for your data to first appear within the Scout UI.

Tasks will appear in the "Background Jobs" area of the Scout UI.

## Heroku Customers

If you've installed Scout via the Heroku Addon, the provisioning process automatically sets `SCOUT_MONITOR` and `SCOUT_KEY` via config vars. Only `SCOUT_NAME` is additionally required.

## Documentation

For more information, visit: https://scoutapm.com/docs/python/other-libraries#rq

