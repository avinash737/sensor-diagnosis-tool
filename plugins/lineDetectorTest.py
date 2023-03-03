import numpy as np
from diagnosis.pluginBase import Test
from logging import Logger
from typing import Optional
from collections import defaultdict
from datetime import datetime
from plugins.helpers.feet_merger import get_merged_data
from plugins.helpers.split_detector import is_split


class LineDetector(Test):
    def __init__(self, config: dict, logger: Logger) -> None:
        super().__init__(config, logger)
        self.data = defaultdict(dict)

    def digest(self, data):
        # TODO copmlete this method
        self.data.update(data)

    def runTest(self, data) -> None:
        self.logger.info("Initiating Line Detector Test")
        self.data = data

        report = self.generateReportData()

        self.logger.info("Report generated")
        self.logger.info("Line detector test complete")

        return report

    def generateReportData(self) -> Optional[dict]:
        
        self.logger.info("Preprocessing data")
        merged_data = get_merged_data(self.data)
        self.logger.info("Initializing report generation")

        today = str(datetime.today().time())

        json_data = defaultdict(dict)
        json_data["testName"] = "Line Detection"
        json_data["testRunTime"] = today

        for date in list(merged_data.keys()):
            date = str(date)
            json_data["sensorDataTime"] = date
            json_data["devices"] = []
            for device in list(merged_data[date].keys()):
                status = "active"
                if (not np.count_nonzero(merged_data[date][device]["leftMerged"]) and not np.count_nonzero
                    (merged_data[date][device]["rightMerged"]
                )):
                    status = "completelyInactive"
                elif not np.count_nonzero(merged_data[date][device]["leftMerged"]):
                    status = "leftInactive"
                elif not np.count_nonzero(merged_data[date][device]["rightMerged"]):
                    status = "rightInactive"
                
                split_data_l = is_split(merged_data[date][device]["leftMerged"])
                split_data_r = is_split(merged_data[date][device]["rightMerged"])

                sensor_data = {
                    device:
                    {
                        "status": status,
                        "details":
                        {
                            "rowsL": split_data_l["rows"],
                            "rowsR": split_data_r["rows"],
                            "colsL": split_data_l["cols"],
                            "colsR": split_data_r["cols"],
                        }
                    }
                }
                json_data["devices"].append(sensor_data)

        return json_data


export = LineDetector