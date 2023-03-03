from copy import deepcopy
import pathlib
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


def show_figure(data, dpi):
    fig, axs = make_figure(dpi)
    axs.imshow(data, vmin=0, vmax=255, interpolation=None)
    plt.show()


def make_figure(dpi):
    fig = plt.figure(frameon=True, figsize=(480 / dpi, 1056 / dpi))
    axs = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    axs.set_axis_off()
    fig.add_axes(axs)

    return fig, axs


def denoise(data):
    data = refine_edges(data.T)
    data = refine_edges(data.T)

    return data


def refine_edges(data):
    new_data = deepcopy(data)

    for i in range(len(new_data)):

        if new_data[i][0] and not new_data[i][1]:
            new_data[i][0] = 0

        if new_data[i][-1] and not new_data[i][-2]:
            new_data[i][-1] = 0

        for j, col in enumerate(new_data[i]):

            if (
                np.count_nonzero(new_data[i - 1 : i + 2][j - 1 : j + 2]) == 1
                and new_data[i][j]
            ):
                new_data[i][j] = 0

            if (
                (j < (len(new_data[i]) - 2))
                and not new_data[i][j]
                and new_data[i][j + 1]
                and not new_data[i][j + 2]
            ):
                new_data[i][j + 1] = 0
            elif (
                (j < (len(new_data[i]) - 3))
                and not new_data[i][j]
                and new_data[i][j + 1]
                and new_data[i][j + 2]
                and not new_data[i][j + 3]
            ):
                new_data[i][j + 1 : j + 3] = 0
            elif (
                (j < (len(new_data[i]) - 4))
                and not new_data[i][j]
                and new_data[i][j + 1]
                and new_data[i][j + 2]
                and new_data[i][j + 3]
                and not new_data[i][j + 4]
            ):
                new_data[i][j + 1 : j + 4] = 0

    return new_data


def save_figure(data, savepath):
    fig, axs = make_figure(96)

    axs.imshow(data)
    plt.savefig(savepath)
    plt.close(fig)


def pad_image(frame, max_row, max_col):
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]
    padding_height = np.int0(abs(max_row - frame_height) / 2)
    padding_width = np.int0(abs(max_col - frame_width) / 2)
    frame = np.pad(
        frame,
        ((padding_height, padding_height), (padding_width, padding_width)),
    )
    if frame.shape[0] < max_row:
        frame = np.pad(frame, ((0, 1), (0, 0)))
    if frame.shape[1] < max_col:
        frame = np.pad(frame, ((0, 0), (0, 1)))

    return frame


def separate_toe_from_foot(data):

    new_data = deepcopy(data)

    smallest_row_len = len(new_data[0])

    smallest_row_idx = []

    top_point = len(new_data) - 1
    bottom_point = 0

    for i in range(len(new_data)):
        if new_data[i].any():
            top_point = i

    for i in range(len(new_data)):
        if new_data[i].any():
            bottom_point = i
            break

    for i in range(len(new_data) // 2, 0, -1):
        if (
            new_data[i].any()
            and np.count_nonzero(new_data[i]) <= smallest_row_len
            and i is not bottom_point
        ):
            smallest_row_len = np.count_nonzero(new_data[i])

    for i in range(len(new_data) // 2, 0, -1):
        if np.count_nonzero(new_data[i]) == smallest_row_len:
            smallest_row_idx.append(i)

    if not np.array(smallest_row_idx).any():
        smallest_row_idx.append(1)

    new_data[0 : smallest_row_idx[0]] = np.zeros(len(new_data[0]))

    return new_data


def rotate_image(data, angle):

    midpoint = np.array([2 * data.shape[1] // 2, 2 * data.shape[0] // 2])

    new_data = np.zeros((2 * data.shape[0], 2 * data.shape[1]))

    radians = np.radians(-angle)

    R = np.array(
        [[np.cos(radians), np.sin(radians)], [-np.sin(radians), np.cos(radians)]]
    )

    points = np.argwhere(data > 0)
    points = np.roll(points, 1, axis=1)

    rotated_points = (R @ points.T).T

    rotated_points = np.int0(rotated_points)

    min_x, min_y = np.min(rotated_points, axis=0)
    max_x, max_y = np.max(rotated_points, axis=0)

    for i in rotated_points:
        new_data[i[1] - min_y][i[0] - min_x] = 128

    return new_data


def merge_images(image1, image2):
    """Merge two images into one, displayed side by side
    :param image1: path to first image file
    :param image2: path to second image file
    :return: the merged Image object
    """
    image1 = pathlib.Path(image1)
    image2 = pathlib.Path(image2)
    im1 = Image.open(image1)
    im2 = Image.open(image2)

    max_height = max(im1.height, im2.height)

    dst = Image.new("RGB", (im1.width + im2.width, max_height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst
