from diagnosis.pluginBase import Data, Source
from typing import List
from logging import Logger
from pymongo import MongoClient
from collections import defaultdict
from plugins.helpers import file_handler


class Connector():

    # Connector class to establish connection with MongoDB
    def __init__(self, config: dict, logger: Logger) -> None:
        self.__client = self.__connect()
        self.__config = config
        self.logger = logger

    def __connect(self):
        return MongoClient(self.url)
    
    def get_db(self):
        return self.__client[self.__config["source"]["db"]]

    def get_collection(self, collection: str):
        col = self.__client[self.__config["source"]["db"]].get_collection(collection)
        return col


class MongoDbSource(Source):

    # since the constructor can not use any other arguments we
    # could just leave it out and have our class inherit the
    # constructor from Source, which just saves config+ logger.
    # But we want to validate the config section for our plugin,
    # so we do this here in the init, after passing config and
    # logger to the inherited constructor method.
    def __init__(self, config: dict, logger: Logger, start_date, end_date) -> None:
        super().__init__(config, logger)
        try:
            self.url = self.config["url"]
            self.hours = self.config["hours"]
        except KeyError as e:
            self.logger.error(f"Config is missing section {e}.")
            exit(2)
        self.conn = Connector()
        self.start_date = start_date
        self.end_date = end_date

    def getData(self) -> List[Data]:

        # Get collections from the db

        self.logger.info("Preparing dataset")

        binariesData = self.conn.get_collection("binaries")
        devicesData = self.conn.get_collection("devices")
        measData = self.conn.get_collection("measurements")

        data = defaultdict(list)

        for measurement in measData:
            date = measurement["meta"]["timeMeasurement"]
            deviceId = measurement["device"]

            if self.start_date != "-1":
                if date < self.start_date:
                    continue

            if self.end_date != "-1":
                if date > self.end_date:
                    continue

            if date not in list(data.keys()):
                data[date] = {}
            for device in devicesData:
                if device["_id"] == deviceId:
                    deviceName = device["macAddress"]
                    if deviceName not in list(data[date].keys()):
                        data[date][deviceName] = {"LDatContent": [], "RDatContent": []}
            for binary in measurement["binaries"]:
                binaryId = binary
                binaryData = binariesData.find({"_id": binaryId})
                LData = file_handler.read_foot_matrix_short_from_bson_binary(binaryData["LDatContent"])
                RData = file_handler.read_foot_matrix_short_from_bson_binary(binaryData["RDatContent"])
                data[date][deviceName]["LDatContent"].append(LData)
                data[date][deviceName]["RDatContent"].append(RData)
        
        self.logger.info("Data ready")
        
        return data
        

export = MongoDbSource
