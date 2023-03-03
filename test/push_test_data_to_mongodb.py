import pathlib
import time
import numpy as np
import pandas as pd
import struct
import gzip
import os
import sys
import warnings
import shutil
import base64
from datetime import datetime
from pymongo import MongoClient
from bson.binary import Binary
import tomli
import os
from os import environ as env
from collections import defaultdict


class Connector:
    def __init__(self) -> None:
        CONFIG_PATH = os.path.abspath(
            env.get(
                "CONFIG_PATH",
                "C:/Users/avina/Documents/Incoretex/deichmann_diagnosis_tool/config/config.toml",
            )
        )
        with open(CONFIG_PATH, "r") as f:
            config = tomli.loads(f.read())
        self.__config = config
        self.url = self.__config["source"]["url"]
        self.__client = self.__connect()

    def __connect(self):
        return MongoClient(self.url)

    def get_db(self):
        return self.__client[self.__config["source"]["db"]]

    def get_collections(self, collection: str):
        collections = self.__client[self.__config["source"]["db"]][collection].find()
        return collections

    def get_collection(self, collection: str):
        col = self.__client[self.__config["source"]["db"]].get_collection(collection)
        return col

    def post_data(self, db: str, collection: str, data: dict):
        collection = self.__client[db][collection]
        post_id = collection.insert_one(data).inserted_id
        return post_id

    def client(self):
        return self.__client


# TODO:
# 1. Upload devices only once
# 2. create binaries and measurements in the loop
# 3. Instead of saving them in the folder locally publish them to the test database


FOLDER = "data/data_device_check_test_new"
devices = {
    "e45f0192da22": {"rows": [32, 45, 65, 66, 67, 87], "cols": [45, 56, 67, 78, 89]},
    "e450192dabd": {
        "rows": [41, 57, 61, 90, 91, 92],
        "cols": [36, 76, 43, 95, 155, 157, 158],
    },
    "e450192da7e": {
        "rows": [51, 53, 54, 61, 62, 92],
        "cols": [36, 42, 43, 44, 153, 155, 157, 158],
    },
}

ROWS = 352
COLS = 160


def read_foot_matrix(filename: str, rows: int, cols: int) -> np.ndarray:
    matrix: np.ndarray = np.empty((rows, cols), dtype=np.int16)

    with gzip.open(filename, "rb") as f:
        for i in range(rows):
            for j in range(cols):
                try:
                    matrix[i][j] = struct.unpack("!h", f.read(2))[0]
                except:
                    matrix[i][j] = 0

    return matrix


def read_binary_foot_matrix(filename: str, rows: int, cols: int):
    bin_data = ""

    with gzip.open(filename, "rb") as f:
        bin_data = f.read()

    return bin_data


def read_foot_matrix_short_from_binary(data, rows: int, cols: int) -> np.ndarray:
    matrix: np.ndarray = np.empty((rows, cols), dtype=np.int16)

    for i in range(rows):
        for j in range(cols):
            try:
                matrix[i][j] = struct.unpack("!h", data)[0]
            except:
                matrix[i][j] = 0

    return matrix


def write_foot_matrix(filename: str, matrix: np.ndarray, rows: int, cols: int):
    with gzip.open(filename, "wb") as f:
        for i in range(rows):
            for j in range(cols):
                struct.pack("!h", matrix[i][j])


def create_defect(datfile, rows, cols):
    mat = read_foot_matrix(datfile, ROWS, COLS)
    mat[:, cols] = 0
    mat[rows, :] = 0
    return mat


def upload_device(connector, db, collection, device_id):
    data = {"macAddress": device_id}
    return connector.post_data(db, collection, data)


def upload_binaries(connector, db, collection, data):
    data = {"LDatFileName": data["LDatFileName"], "RDatFileName": data["RDatFileName"], "LDatContent": data["LDatContent"], "RDatContent": data["RDatContent"]}
    # data = {"content": data["content"], "fileName": data["fileName"]}
    return connector.post_data(db, collection, data)


def upload_measurement(connector, db, collection, deviceId, binaryId, meta):
    data = {
        "meta": meta,
        "device": deviceId,
        "binaries": binaryId,
    }
    return connector.post_data(db, collection, data)


def get_measurements_data(input):
    measData = []
    devices = []

    conn = Connector()

    binCol = conn.get_collection("binaries")
    devCol = conn.get_collection("devices")

    path = input
    device_list = os.listdir(path)

    for device in device_list:

        tempData = defaultdict(dict)
        for doc in devCol.find({"macAddress": device}):
            tempData["device"] = doc["_id"]
        tempData["binaries"] = []
        # To save today's date
        # tempData["meta"] = {"timeMeasurement": datetime.timestamp(datetime.now())}

        if (
            "outputs" in device
            or "Image" in device
            or "Failed" in device
            or "Rejected" in device
            or "diag" in device
            or "report" in device
        ):
            continue

        devices.append(device)
        device_folder = pathlib.Path(str(path) + "/" + str(device))
        folders_list = os.listdir(device_folder)

        for folder in folders_list:

            if (
                "outputs" in folder
                or "Image" in folder
                or "Failed" in folder
                or "Rejected" in folder
                or "diag" in folder
                or "report" in folder
            ):
                continue

            folder_path = pathlib.Path(str(device_folder) + "/" + str(folder))
            files_list = os.listdir(folder_path)

            if len(list(files_list)) < 2:
                continue

            left_file = None
            right_file = None

            for file in files_list:
                if "LnewDat" in file or "Ldat" in file:
                    left_file = file
                    left_filepath = pathlib.Path(
                        str(path)
                        + "/"
                        + str(device)
                        + "/"
                        + str(folder)
                        + "/"
                        + str(left_file)
                    )
                    file_mtime = os.path.getmtime(left_filepath)
                    file_mtime = time.ctime(file_mtime)
                    file_mtime = datetime.strptime(file_mtime, "%c")
                    file_mtime = datetime.strftime(file_mtime, "%Y-%m-%d")
                if "RnewDat" in file or "Rdat" in file:
                    right_file = file
                    right_filepath = pathlib.Path(
                        str(path)
                        + "/"
                        + str(device)
                        + "/"
                        + str(folder)
                        + "/"
                        + str(right_file)
                    )
                    file_mtime = os.path.getmtime(right_filepath)
                    file_mtime = time.ctime(file_mtime)
                    file_mtime = datetime.strptime(file_mtime, "%c")
                    file_mtime = datetime.strftime(file_mtime, "%Y-%m-%d")
                    tempData["modTime"] = file_mtime

            tempBin = binCol.find({"LDatFileName": left_file, "RDatFileName": right_file})
            tempDev = devCol.find({"macAddress": device})
            # To save modified time of the data
            tempData["meta"] = {"timeMeasurement": file_mtime}
            for doc in tempBin:
                tempData["binaries"].append(doc["_id"])
            # for doc in tempDev:
            #     tempData["device"].append(doc["_id"])

        measData.append(tempData)

    return measData


def get_binaries_data(input):

    binData = defaultdict(dict)

    devices = []

    path = input
    device_list = os.listdir(path)

    for device in device_list:

        binData[device] = []

        if (
            "outputs" in device
            or "Image" in device
            or "Failed" in device
            or "Rejected" in device
            or "diag" in device
            or "report" in device
        ):
            continue

        devices.append(device)
        device_folder = pathlib.Path(str(path) + "/" + str(device))
        folders_list = os.listdir(device_folder)

        for folder in folders_list:

            if (
                "outputs" in folder
                or "Image" in folder
                or "Failed" in folder
                or "Rejected" in folder
                or "diag" in folder
                or "report" in folder
            ):
                continue

            folder_path = pathlib.Path(str(device_folder) + "/" + str(folder))
            files_list = os.listdir(folder_path)

            if len(list(files_list)) < 2:
                continue

            left_file = None
            right_file = None

            for file in files_list:
                if "LnewDat" in file or "Ldat" in file:
                    left_file = file
                    left_filepath = pathlib.Path(
                        str(path)
                        + "/"
                        + str(device)
                        + "/"
                        + str(folder)
                        + "/"
                        + str(left_file)
                    )
                    left_binary = read_foot_matrix(left_filepath, ROWS, COLS)
                    # left_binary = left_binary.encode("utf-8")
                    left_binary = Binary(left_binary, 0)
                if "RnewDat" in file or "Rdat" in file:
                    right_file = file
                    right_filepath = pathlib.Path(
                        str(path)
                        + "/"
                        + str(device)
                        + "/"
                        + str(folder)
                        + "/"
                        + str(right_file)
                    )
                    right_binary = read_foot_matrix(right_filepath, ROWS, COLS)
                    # right_binary = right_binary.encode("utf-8")
                    right_binary = Binary(right_binary, 0)

            binData[device].append(
                {"LDatFileName": left_file, "RDatFileName": right_file, "LDatContent": left_binary, "RDatContent": right_binary}
            )

    return binData


def main(input):
    binDataL = []
    binDataR = []
    try:
        os.mkdir(pathlib.Path(input).parent.joinpath(FOLDER))
    except Exception as e:
        print(e)
        warnings.warn("folder already exists, moving on")
        pass

    for folder in pathlib.Path(input).iterdir():
        if (
            "outputs" in folder.name
            or "Image" in folder.name
            or "Failed" in folder.name
            or "Rejected" in folder.name
            or "diag" in folder.name
            or "report" in folder.name
        ):
            continue
        else:
            dest = np.random.choice(list(devices.keys()))
            print(dest)
            try:
                os.mkdir(pathlib.Path(FOLDER).joinpath(dest))
            except Exception as e:
                print(e)
                pass
            try:
                os.mkdir(
                    pathlib.Path(input)
                    .parent.joinpath(FOLDER)
                    .joinpath(dest)
                    .joinpath(folder.name)
                )
            except Exception as e2:
                print(e2)
                pass
        for file in (
            pathlib.Path(FOLDER).joinpath(dest).joinpath(folder).rglob("*.Ldat")
        ):
            m = create_defect(file, devices[dest]["rows"], devices[dest]["cols"])
            binDataL.append(read_binary_foot_matrix(file, ROWS, COLS))
            write_foot_matrix(
                pathlib.Path(input)
                .parent.joinpath(FOLDER)
                .joinpath(dest)
                .joinpath(folder.name)
                .joinpath(file.name.split(".")[0] + ".LnewDat"),
                m,
                ROWS,
                COLS,
            )
        for file in (
            pathlib.Path(FOLDER).joinpath(dest).joinpath(folder).rglob("*.Rdat")
        ):
            m = create_defect(file, devices[dest]["rows"], devices[dest]["cols"])
            binDataR.append(read_binary_foot_matrix(file, ROWS, COLS))
            write_foot_matrix(
                pathlib.Path(input)
                .parent.joinpath(FOLDER)
                .joinpath(dest)
                .joinpath(folder.name)
                .joinpath(file.name.split(".")[0] + ".RnewDat"),
                m,
                ROWS,
                COLS,
            )


if __name__ == "__main__":
    input = "C:/Users/avina/Documents/Incoretex/deichmann_diagnosis_tool/data/run1_7_0SplittedData_FrameByFrame"
    conn = Connector()
    db = "AviTestDB"
    device_ids = list(devices.keys())

    # binData = get_binaries_data(input)

    # # for device_id in device_ids:
    # #     # DEVICES
    # #     # DONE
    # #     # upload_device(conn, db, "devices", device_id)
    # #     for i in binData[device_id]:
    # #         # BINARIES
    # #         # DONE
    # #         # upload_binaries(conn, db, "binaries", i)
    # #         pass

    # measData = get_measurements_data(input)

    # # MEASUREMENTS
    # # for data in measData:
    # #     # DONE
    # #     upload_measurement(
    # #         conn, db, "measurements", data["device"], data["binaries"], data["meta"]
    # #     )
    # #     pass

    print("TEST DB UPLOAD COMPLETED")
