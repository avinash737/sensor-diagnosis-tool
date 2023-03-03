import click
import tomli
import os
import sys
from typing import Dict, Type
from os import environ as env
import colorama
from datetime import datetime
from collections import defaultdict
from plugins import lineDetectorTest as ldTest, source as src, sink as snk

colorama.init()
from log import logger  # use this logger for everything! no print calls!

from pluginBase import (
    Source,
    Sink,
    Test,
    Plugin,
)  # abstract classes for plugins
from pluginHelpers import loadPlugin, verifyPlugin

# Load the paths for config and plugins and make sure they exist and can be imported from
CONFIG_PATH = os.path.abspath(env.get("CONFIG_PATH", "./config/config.toml"))
PLUGINS_PATH = os.path.abspath(env.get("PLUGINS_PATH", "./plugins"))
logger.debug(f"CONFIG_PATH={CONFIG_PATH}")
logger.debug(f"PLUGINS_PATH={PLUGINS_PATH}")
os.makedirs(PLUGINS_PATH, exist_ok=True)
sys.path.append(PLUGINS_PATH)


def format_date(date):
    date = str(date)

    if date != "-1":
        date = datetime.strptime(date, "%Y-%m-%d")
        date = datetime.strftime(date, "%Y-%m-%d")
    
    return date


@click.group(help="Performs several checks and tests on Deichmann data")
def cli():
    pass


@cli.command(help="Used for non-interactive Docker mode")
@click.option(
    "--start_date",
    default=datetime.today().date(),
    help="Give the date (YYYY-MM-DD) from when the data will be checked. -1 for all.",
)
@click.option(
    "--end_date",
    default=datetime.today().date(),
    help="Give the date (YYYY-MM-DD) till when the data will be checked. -1 for all.",
)
def headless(start_date=datetime.today().date(), end_date=datetime.today().date()):

    # TIME FORMATTING

    start_date = format_date(start_date)
    end_date = format_date(end_date)

    logger.info("Starting headless mode...")
    # Load and parse config file
    logger.debug(f'Loading config from "{CONFIG_PATH}".')
    if not os.path.exists(CONFIG_PATH):
        logger.error(f'Config at "{CONFIG_PATH}" does not exist.')
        exit(1)
    with open(CONFIG_PATH, "r") as f:
        config = tomli.loads(f.read())

    # Validate configuration
    try:
        config["source"]["plugin"]
        config["sink"]["plugin"]
        config["tests"]
        config["general"]["headless"]
    except KeyError as e:
        logger.error(f"Config is missing a section {e} somewhere.")
        exit(1)

    logger.debug("Config successfully loaded.")

    # load and verify plugin classes for source and sink
    sourcePlugin: Type[Source] = verifyPlugin(loadPlugin(config["source"]["plugin"]), Source)  # type: ignore
    logger.info(f"Using {sourcePlugin.__name__} plugin as source.")
    sinkPlugin: Type[Sink] = verifyPlugin(loadPlugin(config["sink"]["plugin"]), Sink)  # type: ignore
    logger.info(f"Using {sinkPlugin.__name__} plugin as sink.")

    # Now, we load all the test plugins specified in the config file
    testPlugins: Dict[str, Type[Test]] = {}
    for testName in config["tests"]:
        try:
            testPlugin: Type[Test] = verifyPlugin(loadPlugin(config["tests"][testName]["plugin"]), Test)  # type: ignore
            logger.debug(f"Loaded test '{testPlugin.__name__}' plugin as '{testName}'.")
            # if the section does not have a plugin property -> abort
        except KeyError:
            logger.error(f"Test section 'tests.{testName}' has no 'plugin' property.")
            exit(1)

        # otherwise, add the test
        logger.debug(f"Adding test '{testPlugin.__name__}' as '{testName}'.")
        testPlugins[testName] = testPlugin
    logger.info(f"Loaded {len(testPlugins)} tests.")

    # MAIN LOOP

    # instantiate plugins
    source = sourcePlugin(config=config["source"], logger=logger, start_date=start_date, end_date=end_date)
    logger.debug(f"Instantiated source '{sourcePlugin.__name__}'.")
    sink = sinkPlugin(config=config["sink"], logger=logger)
    logger.debug(f"Instantiated sink '{sinkPlugin.__name__}'.")

    tests: Dict[str, Test] = {}
    for name, plugin in testPlugins.items():
        tests[name] = plugin(config["tests"][name], logger=logger)
        logger.debug(f"Instantiated test '{name}'.")

    # SOURCE
    # Currently this calls the plugin from source.py
    source = src.MongoDbSource(config, logger, start_date, end_date)
    data = source.getData()

    # TESTS
    report = defaultdict(list)
    report["testReports"] = []

    # for test in tests:
    #     report["testReports"].append(test.runTest(data))

    # LINE DETECTOR TEST
    # Currently this calls the plugin from lineDetectorTest.py
    test = ldTest.LineDetector(config, logger)
    report["testReports"].append(test.runTest(data))
    
    logger.info("All tests complete")

    # SINK
    sink = snk.MongoDbSink(config, logger)
    sink.processReport(report)

    logger.info("All reports processed and uploaded")

if __name__ == "__main__":
    cli()
