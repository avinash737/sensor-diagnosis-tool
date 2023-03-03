import struct, gzip
import numpy as np


def read_foot_matrices_int(
    filename: str, count: int, rows: int, cols: int
) -> np.ndarray:
    matrix = np.zeros((count, rows, cols), dtype=np.int32)

    with gzip.open(filename, "rb") as f:
        for x in range(count):
            for i in range(rows):
                for j in range(cols):
                    try:
                        matrix[x][i][j] = struct.unpack("!i", f.read(4))[0]
                    except:
                        matrix[x][i][j] = 0

    return matrix


def read_array_int(filename: str, length: int) -> np.ndarray:
    matrix: np.ndarray = np.empty(length, dtype=np.int32)

    with gzip.open(filename, "rb") as f:
        for i in range(length):
            try:
                matrix[i] = struct.unpack("!i", f.read(4))[0]
            except:
                matrix[i] = 0

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


def read_foot_matrix_int(filename: str, rows: int, cols: int) -> np.ndarray:
    matrix: np.ndarray = np.empty((rows, cols), dtype=np.int32)

    with gzip.open(filename, "rb") as f:
        for i in range(rows):
            for j in range(cols):
                try:
                    matrix[i][j] = struct.unpack("!i", f.read(4))[0]
                except:
                    matrix[i][j] = 0

    return matrix


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


def read_foot_matrices_short(
    filename: str, count: int, rows: int, cols: int
) -> np.ndarray:
    matrix: np.ndarray = np.empty((count, rows, cols), dtype=np.int16)

    with gzip.open(filename, "rb") as f:
        for k in range(count):
            for i in range(rows):
                for j in range(cols):
                    try:
                        matrix[k][i][j] = struct.unpack("!h", f.read(2))[0]
                    except:
                        matrix[k][i][j] = 0

    return matrix
