from collections import defaultdict
import numpy as np
from .figure_handler import denoise


def get_merged_data(data):
    """
    Merge all data belonging to the same date and then save the combined data with all feet
    """

    merged_data = defaultdict(list)

    for date in list(data.keys()):
        merged_data[date] = {}
        for device in list(data[date].keys()):
            merged_data[date][device] = {"leftMerged": {}, "rightMerged": {}}

            # Left Feet
            
            merged_foot = np.zeros_like(data[date][device]["LDatContent"][0])
            for foot in data[date][device]["LDatContent"]:
                foot = denoise(foot)
                merged_foot = np.add(merged_foot, foot)

            merged_data[date][device]["leftMerged"] = merged_foot

            # Right Feet

            merged_foot = np.zeros_like(data[date][device]["RDatContent"][0])
            for foot in data[date][device]["RDatContent"]:
                foot = denoise(foot)
                merged_foot = np.add(merged_foot, foot)

            merged_data[date][device]["rightMerged"] = merged_foot

    return merged_data
