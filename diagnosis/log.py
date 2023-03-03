from os import environ as env
import os
import colorama
import click
import sys
import logging

# Make sure the log folder exists by creating it with os.makedirs
LOG_FOLDER = os.path.abspath(env.get("LOG_FOLDER", "./logs/"))
LOG_LEVEL = logging._nameToLevel.get(env.get("LOG_LEVEL", "INFO"), logging.INFO)
NO_COLOR = int(env.get("NO_COLOR", "0")) == 1
os.makedirs(LOG_FOLDER, exist_ok=True)

# This is the logging format
baseFormat = '%(asctime)s %(levelname)s[%(module)s] : %(message)s'

# Add a file handler to write logs to file
filehandler = logging.FileHandler(os.path.join(LOG_FOLDER,"dm-diagnosis.log"))
filehandler.setFormatter(logging.Formatter(baseFormat))
filehandler.setLevel(logging.DEBUG)

# Custom formatter which dies color coding for better readability in CLI log output
class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: lambda x: click.style(x, fg="blue"),
        logging.INFO: lambda x: x,
        logging.WARNING: lambda x: click.style(x, fg="yellow"),
        logging.ERROR: lambda x: click.style(x, fg="red"),
        logging.CRITICAL: lambda x: click.style(x, fg="yellow", bg="red"),
    }

    def format(self, record):
        return self.FORMATS[record.levelno](logging.Formatter(baseFormat).format(record))
        # return logging.Formatter(self.FORMATS.get(record.levelno)).format(record)

# Add stream handler for stdout log
stdoutHandler = logging.StreamHandler(sys.stdout)
stdoutHandler.setFormatter(logging.Formatter(baseFormat) if NO_COLOR else CustomFormatter())
stdoutHandler.setLevel(logging.DEBUG)

# Add another stream handler only for error log to stderr
stderrHandler = logging.StreamHandler(sys.stderr)
stderrHandler.setFormatter(logging.Formatter(baseFormat) if NO_COLOR else CustomFormatter())
stderrHandler.setLevel(logging.ERROR)

# Create the logger add add all the handlers to it.
# Only the logger get's the desired log level setting!
logger = logging.getLogger("dm-diagnosis")
logger.setLevel(logging.DEBUG)
logger.addHandler(filehandler)
logger.addHandler(stdoutHandler)
logger.addHandler(stderrHandler)

# When using colorama, we should init the TTY
if not NO_COLOR: colorama.init()
