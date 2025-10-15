# Scout APM Setup for Dramatiq

## Installation

Scout supports Dramatiq 1.0+.

### Step 1: Install the scout-apm package

```bash
pip install scout-apm
```

### Step 2: Add Scout to your Dramatiq broker

```python
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from scout_apm.dramatiq import ScoutMiddleware
from scout_apm.api import Config

# Configure Scout
Config.set(
    key="{SCOUT_KEY}",
    name="{APP_NAME}",
    monitor=True,
)

# Create broker with Scout middleware
broker = RabbitmqBroker()
broker.add_middleware(ScoutMiddleware())
dramatiq.set_broker(broker)
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

For more information, visit: https://scoutapm.com/docs/python/other-libraries#dramatiq

