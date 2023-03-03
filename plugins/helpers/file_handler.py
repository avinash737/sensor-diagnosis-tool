import json
from collections import defaultdict
import pathlib
from datetime import datetime
import struct, gzip
import numpy as np


def get_dict_from_json(json_file_path):
    data = defaultdict(dict)
    with open(json_file_path) as f:
        try:
            data = json.load(f)
        except:
            data = defaultdict(dict)
    return data


def read_foot_matrix_short(filename: str, rows: int, cols: int) -> np.ndarray:
    matrix: np.ndarray = np.empty((rows, cols), dtype=np.int16)

    with gzip.open(filename, "rb") as f:
        for i in range(rows):
            for j in range(cols):
                try:
                    matrix[i][j] = struct.unpack("!h", f.read(2))[0]
                except:
                    matrix[i][j] = 0

    return matrix


def read_foot_matrix_short_from_bson_binary(data, rows: int, cols: int) -> np.ndarray:
    matrix: np.ndarray = np.empty((rows, cols), dtype=np.int16)

    for i in range(rows):
        for j in range(cols):
            try:
                matrix[i][j] = struct.unpack("!h", data)[0]
            except:
                matrix[i][j] = 0

    return matrix


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
