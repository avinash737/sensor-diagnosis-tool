import json
from collections import defaultdict
import pathlib
from datetime import datetime


def get_dict_from_json(json_file_path):
    data = defaultdict(dict)
    with open(json_file_path) as f:
        try:
            data = json.load(f)
        except:
            data = defaultdict(dict)
    return data


def save_report_to_file(report, path):
    pathlib.Path(str(path) + "/diagnosis/").mkdir(parents=True, exist_ok=True)
    pathlib.Path(str(path) + "/diagnosis/lineDetector").mkdir(
        parents=True, exist_ok=True
    )
    savepath = pathlib.Path(path + "/diagnosis/lineDetector/")
    pathlib.Path(str(savepath)).mkdir(parents=True, exist_ok=True)
    savepath = pathlib.Path(
        str(savepath) + "/" + str(datetime.today().date()) + "_report.json"
    )

    with open(savepath, "w") as f:
        json.dump(report, f, indent=4)

    return savepath
