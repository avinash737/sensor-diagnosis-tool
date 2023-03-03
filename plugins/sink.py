from diagnosis.pluginBase import Sink
from logging import Logger
from pymongo import MongoClient

class Connector():
     # Connector class to establish connection with MongoDB
    def __init__(self, config: dict, logger: Logger) -> None:
        self.__client = self.__connect()
        self.__config = config
        self.logger = logger

    def __connect(self):
        return MongoClient(self.url)

    def post_data(self, data: dict):
        collection = self.__config["db"]["collection"]
        post_id = collection.insert_one(data).inserted_id
        return post_id

class MongoDbSink(Sink):
    def __init__(self, config: dict, logger: Logger) -> None:
        super().__init__(config, logger)
        try:
            self.url = self.config["url"]
            self.hours = self.config["hours"]
        except KeyError as e:
            self.logger.error(f"Config is missing section {e}.")
            exit(2)
        self.conn = Connector()
    
    def processReport(self, report: dict) -> None:
        self.logger.info("Processing report")
        self.conn.post_data(report)
        self.logger.info("Report uploaded")


export = MongoDbSink