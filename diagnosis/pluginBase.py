from dataclasses import dataclass
from typing import Dict, List, Optional
from logging import Logger
from abc import abstractmethod


# The data format is as follows:


@dataclass
class Data:
    json: dict
    binaries: Dict[str, bytes]


# These classes are abstract bases for custom plugins.
# However, they only serve the purpose of type checking
# and autocomplete in your IDE.


class Plugin():
    _REQUIRED_METHODS = []


# You NEED to inherit from these classes in order to write
# your own plugin. And you SHOULD implement all the methods
# in your plugin class. See the example plugins.
# All plugins get their config section forwarded to their
# constructor. From there on, it is your responsibility to
# parse your config parameters, as they are completely
# generic and are defined by you.


class Source(Plugin):
    # The source plugin will query/fetch new data from some
    # database / folder / etc. and load it into the required
    # format. The following methods must be implemented in
    # your custom plugin implementation, others are optional:
    _REQUIRED_METHODS = ["getData"]

    # The instance gets all configuration parameters via the
    # config section in the constructor. So no arguments are
    # supplied by the framework except config and logger.
    def __init__(self, config: dict, logger: Logger, start_date, end_date) -> None:
        self.config = config
        self.logger = logger
        self.start_date = start_date
        self.end_date = end_date


    # This will load a chunk of data to be processed. It can be
    # the last 24 hours of measurements, a certain number of
    # measurements, whatever is supplied in your config and
    # whatever you want to implement. The only restriction is the
    # output format of the data in order to guarantee compatibility
    # between the Source and Test plugin instances. This method will
    # be called indefinitely, until an empty list is returned,
    # signaling that there is no more data to fetch.
    @abstractmethod
    def getData(self) -> List[Data]:
        ...

class Test(Plugin):
    # The Test plugin is used to perform the actual analysis of
    # the data. It is created once and data is added for analysis
    # chunk-wise. This allows for parallel analysis across tests.
    # When all data has been give nto the test and the test is done
    # analyzing it. It is asked for the test results and destructed
    # afterwards.
    _REQUIRED_METHODS = ["runTest", "generateReportData"]

    # The instance gets all configuration parameters via the
    # config section in the constructor. So no arguments are
    # supplied by the framework except config and logger.
    # Do not use print() statements! Only the logger!
    def __init__(self, config: dict, logger: Logger) -> None:
        # save the config section for this plugin
        self.config = config
        self.logger = logger

    # Detect missing lines and save the generated error
    # report into a json file in the sepcified format
    @abstractmethod
    def runTest(self) -> None:
        ...

    # digest() is called when new data is fetched from the source.
    # This allows the data source to make multiple fetches and get
    # more data, while previous data is processed, therefore making
    # the process more efficient.
    @abstractmethod
    def digest(self, data: List[Data]) -> None:
        ...

    # This is called when there is no more data to fetch. The main
    # loop tries to collect the results from all the tests via this
    # method. When the test is still performing, just return None.
    # When the test has finished, return a JSON-serializable dict.
    # The containing data can be arbitrary, but must be serializable.
    @abstractmethod
    def generateReportData(self) -> Optional[dict]:
        ...


class Sink(Plugin):
    # The sink plugin will generate reports from the test results
    # and further process them. This may include saving them to a
    # file, sending them somewhere else or performing various checks
    # on the test results. The following methods must be implemented
    # in your custom plugin implementation, others are optional:

    _REQUIRED_METHODS = ["processReport"]

    # The instance gets all configuration parameters via the
    # config section in the constructor. So no arguments are
    # supplied by the framework except config and logger.
    def __init__(self, config: dict, logger: Logger) -> None:
        # save the config section for this plugin
        self.config = config
        self.logger = logger

    # When all test results are collected, and the final report is
    # created, it is passed to this method for saving/sending.
    @abstractmethod
    def processReport(self, report: dict) -> None:
        ...
