# Scout APM Setup for Ruby on Rails

## Installation

The latest `scout_apm` gem supports Rails 3.2+.

### Step 1: Add the Scout gem

Add the `scout_apm` gem to your `Gemfile`:

```ruby
gem 'scout_apm'
```

Then run:

```bash
bundle install
```

### Step 2: Create the configuration file

Create a file at `config/scout_apm.yml` with the following configuration:

```yaml
# Scout APM Configuration for Ruby on Rails
common: &defaults
  # key: Your Organization key for Scout APM. Found on the settings screen.
  key: YOUR_SCOUT_KEY_HERE

  # log_level: Verboseness of logs.
  # - Default: 'info'
  # - Valid Options: debug, info, warn, error
  # log_level: debug

  # use_prepend: Use the newer `prepend` instrumentation method. In some cases, gems
  #              that use `alias_method` can conflict with gems that use `prepend`.
  #              To avoid the conflict, change this setting to match the method
  #              that the other gems use.
  #              If you have another APM gem installed, such as DataDog or NewRelic,
  #              you will likely want to set `use_prepend` to true.
  #
  #              See https://scoutapm.com/docs/ruby/configuration#library-instrumentation-method
  #              for more information.
  # - Default: false
  # - Valid Options: true, false
  # use_prepend: true

  # name: Application name in APM Web UI
  # - Default: the application name comes from the Rails or Sinatra class name
  # name: My Application

  # monitor: Enable Scout APM or not
  # - Default: none
  # - Valid Options: true, false
  monitor: true

production:
  <<: *defaults

development:
  <<: *defaults
  monitor: false

test:
  <<: *defaults
  monitor: false

staging:
  <<: *defaults
```

### Step 3: Using Environment Variables (Recommended)

Instead of hardcoding your Scout key in the configuration file, you can use environment variables:

```yaml
# config/scout_apm.yml
common: &defaults
  key: <%= ENV['SCOUT_KEY'] %>
  name: <%= ENV['SCOUT_NAME'] || 'My Rails App' %>
  monitor: true

production:
  <<: *defaults

development:
  <<: *defaults
  monitor: false

test:
  <<: *defaults
  monitor: false
```

Then set the environment variables:

```bash
export SCOUT_KEY=your_scout_key_here
export SCOUT_NAME="My Rails Application"
```

### Step 4: Deploy

Deploy your application. It takes approximately five minutes for your data to first appear within the Scout UI.

## Configuration Options

### use_prepend

If you have another APM gem installed (DataDog, NewRelic, etc.), you may need to enable `use_prepend`:

```yaml
common: &defaults
  key: <%= ENV['SCOUT_KEY'] %>
  use_prepend: true
  monitor: true
```

### Disabling Monitoring in Specific Environments

The example above shows monitoring disabled in development and test environments. Adjust as needed for your setup.

## Heroku Customers

If you've installed Scout via the Heroku Addon, the provisioning process automatically sets `SCOUT_MONITOR` and `SCOUT_KEY` via config vars. Only `SCOUT_NAME` is additionally required.

## Documentation

For more information, visit: https://scoutapm.com/docs/ruby/configuration
