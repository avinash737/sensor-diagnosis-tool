import numpy as np
from collections import defaultdict


# Algorithms to detect empty rows and cols in sensor
def check_row_split(data):
    """
    Check if there are missing rows in an image
    """
    up, down = 0, len(data) - 1

    for i in range(len(data)):
        if np.count_nonzero(data[i]):
            up = i
            break

    for i in range(len(data) - 1, 0, -1):
        if np.count_nonzero(data[i]):
            down = i
            break

    empty_indices = []

    for i in range(up, down, 1):
        if not np.count_nonzero(data[i]):
            empty_indices.append(i)

    return empty_indices


def is_split(foot_data):
    """
    Check if there are missing rows and columns in an image
    """
    split_data = defaultdict(dict)
    if not np.count_nonzero(foot_data):
        return split_data
    rows = check_row_split(foot_data)
    columns = check_row_split(foot_data.T)

    split_data = {"rows": rows, "cols": columns}

    return split_data


def is_narrow(foot_data):
    """
    Check if the data is too narrow and is cutoff on one side
    """
    data = foot_data.T
    up, down = 0, len(data) - 1

    for i in range(len(data)):
        if np.count_nonzero(data[i]):
            up = i
            break

    for i in range(len(data)):
        if np.count_nonzero(data[i]):
            down = i

    width = down - up + 1

    if width < 60:
        return 1

    return 0
