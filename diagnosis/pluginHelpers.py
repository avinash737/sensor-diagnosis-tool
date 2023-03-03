import importlib
from typing import Type
import colorama

colorama.init()

from log import logger
from pluginBase import Plugin


def loadPlugin(path: str) -> Type[Plugin]:
    logger.debug(f"Loading plugin from '{path}'.")
    try:
        return importlib.import_module(path).export

    except ModuleNotFoundError:
        logger.error(f"Plugin '{path}' cannot be found.")
        exit(1)
    except AttributeError:
        logger.error(f"Plugin '{path}' does not have 'export' property.")
        exit(1)


def verifyPlugin(plugin: Type[Plugin], pluginBaseClass: Type[Plugin]) -> Type[Plugin]:
    # check weather we inherit from the specified base class (Sink,Source,Test,...)
    if pluginBaseClass != None and not issubclass(plugin, pluginBaseClass):
        logger.error(
            f"Plugin '{plugin.__name__}' does not inherit from '{pluginBaseClass.__name__}'."
        )
        exit(1)

    # check weather all required methods are overloaded
    missing = [
        x for x in pluginBaseClass._REQUIRED_METHODS if x not in plugin.__dict__.keys()
    ]
    if missing:
        logger.error(f"Plugin '{plugin.__name__}' is missing attributes: {missing}.")
        exit(1)
    return plugin
