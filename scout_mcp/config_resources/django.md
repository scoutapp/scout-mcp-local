# Scout APM Setup for Django

## Installation

The latest `scout-apm` package supports Django 3.2+.

### Step 1: Install the scout-apm package

```bash
pip install scout-apm
```

### Step 2: Configure Scout in your settings.py file

Add Scout to your `INSTALLED_APPS` **at the beginning** of the list:

```python
# settings.py
INSTALLED_APPS = [
    "scout_apm.django",  # should be listed first
    # ... other apps ...
]
```

### Step 3: Add Scout settings

Add these settings to your `settings.py`:

```python
# Scout settings
SCOUT_MONITOR = True
SCOUT_KEY = "{SCOUT_KEY}"
SCOUT_NAME = "{APP_NAME}"
```

**Alternative: Using Environment Variables**

Instead of hardcoding values in `settings.py`, you can use environment variables:

```python
import os

SCOUT_MONITOR = os.environ.get('SCOUT_MONITOR', 'True').lower() == 'true'
SCOUT_KEY = os.environ.get('SCOUT_KEY', '')
SCOUT_NAME = os.environ.get('SCOUT_NAME', '{APP_NAME}')
```

Then set these environment variables:
- `SCOUT_MONITOR=true`
- `SCOUT_KEY={SCOUT_KEY}`
- `SCOUT_NAME={APP_NAME}`

### Step 4: Middleware (Optional - for better profiling)

Scout automatically inserts its middleware into your settings on Django startup. However, if you need to customize the middleware order or prevent automatic insertion, you can include the Scout middleware classes manually.

**For Django 1.10+ (new-style middleware with MIDDLEWARE setting):**

```python
# settings.py
MIDDLEWARE = [
    # ... any middleware to run first ...
    "scout_apm.django.middleware.MiddlewareTimingMiddleware",
    # ... your normal middleware stack ...
    "scout_apm.django.middleware.ViewTimingMiddleware",
    # ... any middleware to run last ...
]
```

**For Django < 2.0 (old-style middleware with MIDDLEWARE_CLASSES):**

```python
# settings.py
MIDDLEWARE_CLASSES = [
    # ... any middleware to run first ...
    "scout_apm.django.middleware.OldStyleMiddlewareTimingMiddleware",
    # ... your normal middleware stack ...
    "scout_apm.django.middleware.OldStyleViewMiddleware",
    # ... any middleware to run last ...
]
```

**Important:** Anything included before the first middleware timing middleware will not be profiled by Scout. Anything included after the view middleware will be profiled as part of your view, rather than as middleware.

### Step 5: Deploy

Deploy your application. It takes approximately five minutes for your data to first appear within the Scout UI.

## Heroku Customers

If you've installed Scout via the Heroku Addon, the provisioning process automatically sets `SCOUT_MONITOR` and `SCOUT_KEY` via config vars. Only `SCOUT_NAME` is additionally required.

## Documentation

For more information, visit: https://scoutapm.com/docs/python/django
