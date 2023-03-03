# Sensor Diagnosis Tool

## Environment Variables

_All environment variables have default values. So it is not necessary to specify all of them._

| Name  | Usage |
|-------|-------|
| `LOG_FOLDER`  | Where to write log files to
| `LOG_LEVEL`   | One of Python's log levels (as sting)
| `NO_COLOR`    | "1" to disable colored CLI logs
| `CONFIG_PATH` | Path to `.toml` config file
| `PLUGINS_PATH`| Path to the plugin folder where to search for plugins

## Workflow

- Read data from source
- Supply data to all digest plugins / tests
- Generate report
- Send report to sink plugin
