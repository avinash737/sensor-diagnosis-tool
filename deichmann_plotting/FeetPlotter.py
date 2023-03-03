#!/usr/bin/env python
# coding: utf-8

import matplotlib

matplotlib.use("TkCairo")

import matplotlib.pyplot as plt
import os
from os import listdir
from os.path import isfile, join
import re

import json
import shutil

from FeaturePlotter import *
from PlotUtil import *
from JSONWrapper import wrap_namespace
from MatrixReader import read_foot_matrix_short

sensorHeight = 352
mydpi = 96


def plotBaseFeatures(ax, jsonFile, correction):
    plotVInnerBalePoint(ax, jsonFile, correction)
    plotVOuterBalePoint(ax, jsonFile, correction)
    plotVInnerHeelPoint(ax, jsonFile, correction)
    plotMauchLines(ax, jsonFile, correction)
    plotIndicatorLines(ax, jsonFile, correction)
    plotToeBox(ax, jsonFile, correction)
    plotVerticalIndicator(ax, jsonFile.vBottomWMSStart + correction)
    plotHorizontalIndicator(ax)


def showOnlyFoot(footMatrix, dpi):
    fig = plt.figure(frameon=True, figsize=(480 / dpi, 1056 / dpi))
    axs = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    axs.set_axis_off()
    fig.add_axes(axs)
    axs.imshow(footMatrix, vmin=0, vmax=255, interpolation=None)
    plt.show()


def plotBasicFoot(jsonFile, dataSource, footMatrix):
    # setup canvas
    fig = plt.figure(frameon=False, figsize=(480 / mydpi, 1056 / mydpi))
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    fig.add_axes(ax)
    correction = jsonFile[dataSource].bigToeBoundsCorrection
    plotBaseFeatures(ax, jsonFile.leftDebugOutput, correction)
    ax.imshow(footMatrix, interpolation="None")
    return fig, ax, correction


def plotFeetWithClusterCenters(jsonFile, dataSource, footMatrix):
    fig, ax, correction = plotBasicFoot(jsonFile, dataSource, footMatrix)
    plotClusterCenters(ax, jsonFile.leftDebugOutput, correction)
    plotBaseFootCenter(ax, jsonFile.leftDebugOutput, correction)
    return fig, ax, correction


def plotFeetWithContours(jsonFile, dataSource, footMatrix, conMat=None, conMatOpt=None):
    fig, ax, correction = plotBasicFoot(jsonFile, dataSource, footMatrix)
    if conMat != None:
        ax.imshow(conMat, interpolation="None", alpha=0.3, cmap="binary")
    if conMatOpt != None:
        ax.imshow(conMatOpt, interpolation="None", alpha=0.3, cmap="cool")
    return fig, ax, correction


def plotFeetAllCurrentFeatures(
    jsonFile, dataSource, footMatrix, conMat=None, conMatOpt=None
):
    fig, ax, correction = plotBasicFoot(jsonFile, dataSource, footMatrix)
    plotClusterCenters(ax, jsonFile.leftDebugOutput, correction)
    plotBaseFootCenter(ax, jsonFile.leftDebugOutput, correction)
    if conMat != None:
        ax.imshow(conMat, interpolation="None", alpha=0.3, cmap="binary")
    if conMatOpt != None:
        ax.imshow(conMatOpt, interpolation="None", alpha=0.3, cmap="cool")
    return fig, ax, correction


def plotFeetSingle(resultFolder, i):
    try:
        os.makedirs(join(resultFolder, "0_Images"))
    except:
        pass
    onlyfiles = [
        f for f in listdir(join(resultFolder, i)) if isfile(join(resultFolder, i, f))
    ]
    lv = re.compile(".*\.LVdat")
    rv = re.compile(".*\.RVdat")
    j = re.compile(".*\.json")
    cr = re.compile(".*\.Rconmat")
    cl = re.compile(".*\.Lconmat")
    crb = re.compile(".*\.Rbconmat")
    clb = re.compile(".*\.Lbconmat")
    cor = list(filter(cr.match, onlyfiles))
    col = list(filter(cl.match, onlyfiles))
    corb = list(filter(crb.match, onlyfiles))
    colb = list(filter(clb.match, onlyfiles))
    inputLeft = list(filter(lv.match, onlyfiles))
    inputRight = list(filter(rv.match, onlyfiles))
    jfile = list(filter(j.match, onlyfiles))
    with open(join(resultFolder, i, jfile[0])) as f:
        jsonFile = wrap_namespace(json.load(f))
    if jsonFile.analysisResult.rejected == 1:
        try:
            os.makedirs(join(resultFolder, "00_Rejected"))
        except:
            pass
        shutil.copytree(join(resultFolder, i), join(resultFolder, "00_Rejected", i))
        return
    leftFoot = read_foot_matrix_short(
        join(resultFolder, i, inputLeft[0]), sensorHeight, 160
    )
    rightFoot = read_foot_matrix_short(
        join(resultFolder, i, inputRight[0]), sensorHeight, 160
    )
    conMatR = read_foot_matrix_short(join(resultFolder, i, cor[0]), sensorHeight, 160)
    conMatL = read_foot_matrix_short(join(resultFolder, i, col[0]), sensorHeight, 160)
    conMatRB = read_foot_matrix_short(join(resultFolder, i, corb[0]), sensorHeight, 160)
    conMatLB = read_foot_matrix_short(join(resultFolder, i, colb[0]), sensorHeight, 160)
    leftFig, _, _ = plotFeetAllCurrentFeatures(
        jsonFile, "leftDebugOutput", leftFoot, conMatL, conMatLB
    )
    leftFig.savefig(
        join(resultFolder, "0_Images", "LeftFoot{}.png".format(i)), dpi=96, format="png"
    )
    rightFig, _, _ = plotFeetAllCurrentFeatures(
        jsonFile, "rightDebugOutput", rightFoot, conMatR, conMatRB
    )
    rightFig.savefig(
        join(resultFolder, "0_Images", "RightFoot{}.png".format(i)),
        dpi=96,
        format="png",
    )
    plt.close(leftFig)
    plt.close(rightFig)
