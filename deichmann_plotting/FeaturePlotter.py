import matplotlib
import math
from PlotUtil import getClusterColor

matplotlib.use("TkCairo")


def plotVInnerBalePoint(axs, jsondata, correction):
    axs.plot(jsondata.vInnerBalePoint.x, jsondata.vInnerBalePoint.y + correction, "o", markersize=1.5, color="r")
    circle = matplotlib.patches.Circle((jsondata.vInnerBalePoint.x, jsondata.vInnerBalePoint.y + correction), radius=3,
                                       color="r", alpha=0.4)
    axs.add_patch(circle);


def plotVOuterBalePoint(axs, jsondata, correction):
    axs.plot(jsondata.vOuterBalePoint.x, jsondata.vOuterBalePoint.y + correction, "o", markersize=1.5, color="r")
    circle = matplotlib.patches.Circle((jsondata.vOuterBalePoint.x, jsondata.vOuterBalePoint.y + correction), radius=3,
                                       color="r", alpha=0.4)
    axs.add_patch(circle);


def plotVInnerHeelPoint(axs, jsondata, correction):
    axs.plot(jsondata.vInnerHeelPoint.x, jsondata.vInnerHeelPoint.y + correction, "o", markersize=1.5, color="r")
    circle = matplotlib.patches.Circle((jsondata.vInnerHeelPoint.x, jsondata.vInnerHeelPoint.y + correction), radius=3,
                                       color="r", alpha=0.4)
    axs.add_patch(circle);


def plotToeBox(axs, json, correction):
    rect = matplotlib.patches.Rectangle((json.bigToeLeftBounds, json.bigToeUpperBounds + correction),
                                        json.bigToeRightBounds - json.bigToeLeftBounds,
                                        (json.bigToeLowerBounds - json.bigToeUpperBounds), linewidth=1, edgecolor='r',
                                        facecolor='none', alpha=0.3)
    axs.add_patch(rect)
    axs.plot(json.bigToeCenterX, json.bigToeCenterY + correction, "o", markersize=1.5, color="r")
    circle = matplotlib.patches.Circle((json.bigToeCenterX, json.bigToeCenterY + correction), radius=3,
                                       color="r", alpha=0.4)
    axs.add_patch(circle)


def calcLeadVector(jsondata):
    inner = (jsondata.vInnerBalePoint.x, jsondata.vInnerBalePoint.y)
    outer = (jsondata.vOuterBalePoint.x, jsondata.vOuterBalePoint.y)
    lead = (outer[0] - inner[0], outer[1] - inner[1]);
    length = math.sqrt(lead[0] ** 2 + lead[1] ** 2)
    norm = (lead[0] / length, lead[1] / length)
    return norm;


def plotBaleLine(axs, jsondata, leadVector, correction):
    x = [jsondata.vInnerBalePoint.x, jsondata.vInnerBalePoint.x + leadVector[0] * jsondata.vmBaleWidth]
    y = [jsondata.vInnerBalePoint.y + correction,
         jsondata.vInnerBalePoint.y + leadVector[1] * jsondata.vmBaleWidth + correction]
    axs.plot(x, y, "r-", alpha=0.4)


def plotVaultLine(axs, jsondata, leadVector, correction):
    # plot startPoint
    axs.plot(jsondata.vmVaultWidthStart.x, jsondata.vmVaultWidthStart.y + correction, "o", markersize=1.5, color="r")
    startPoint = matplotlib.patches.Circle((jsondata.vmVaultWidthStart.x, jsondata.vmVaultWidthStart.y + correction),
                                           radius=3, color="r", alpha=0.4)
    # plot line
    end = (round(jsondata.vmVaultWidthStart.x + leadVector[0] * jsondata.vmVaultWidth, 1),
           round(jsondata.vmVaultWidthStart.y + leadVector[1] * jsondata.vmVaultWidth + correction, 1))
    axs.plot(end[0], end[1], "o", markersize=1.5, color="r")
    endPoint = matplotlib.patches.Circle((end[0], end[1]), radius=3, color="r", alpha=0.4)

    x = [jsondata.vmVaultWidthStart.x, end[0]]
    y = [jsondata.vmVaultWidthStart.y + correction, end[1]]

    axs.add_patch(startPoint)
    axs.add_patch(endPoint)
    axs.plot(x, y, "r-", alpha=0.4)


def plotHeelLine(axs, jsondata, leadVector, correction):
    axs.plot(jsondata.vmHeelWidthStart.x, jsondata.vmHeelWidthStart.y + correction, "o", markersize=1.5, color="r")
    startPoint = matplotlib.patches.Circle((jsondata.vmHeelWidthStart.x, jsondata.vmHeelWidthStart.y + correction),
                                           radius=3, color="r", alpha=0.4)
    # plot line
    end = (round(jsondata.vmHeelWidthStart.x + leadVector[0] * jsondata.vmHeelWidth, 1),
           round(jsondata.vmHeelWidthStart.y + leadVector[1] * jsondata.vmHeelWidth + correction, 1))
    axs.plot(end[0], end[1], "o", markersize=1.5, color="r")
    endPoint = matplotlib.patches.Circle((end[0], end[1]), radius=3, color="r", alpha=0.4)

    x = [jsondata.vmHeelWidthStart.x, end[0]]
    y = [jsondata.vmHeelWidthStart.y + correction, end[1]]

    axs.add_patch(startPoint)
    axs.add_patch(endPoint)
    axs.plot(x, y, "r-", alpha=0.4)


def plotMauchLines(axs, jsondata, correction):
    leadVector = calcLeadVector(jsondata)
    plotBaleLine(axs, jsondata, leadVector, correction)
    plotVaultLine(axs, jsondata, leadVector, correction)
    plotHeelLine(axs, jsondata, leadVector, correction)


def plotIndicatorLines(axs, jsondata, correction):
    x = [jsondata.vInnerBalePoint.x, jsondata.vInnerHeelPoint.x]
    y = [jsondata.vInnerBalePoint.y + correction, jsondata.vInnerHeelPoint.y + correction]
    axs.plot(x, y, "g--", alpha=0.6)
    # plot bot Line
    x = [0, 160]
    y = [jsondata.vBottomWMSStart + correction, jsondata.vBottomWMSStart + correction]
    axs.plot(x, y, "r:", alpha=0.4)

    y = [jsondata.vTopWMSStart + correction, jsondata.vTopWMSStart + correction]

    axs.plot(x, y, "r:", alpha=0.4)


def plotPredictedTrue(axs, jsondata, correction, true):
    # plot pred and true here
    print("bla")


def plotClusterCenters(axs, jsondata, correction):
    for cluster in jsondata.clusterInformation:
        color = getClusterColor(cluster.classifier)
        axs.plot(cluster.center.x, cluster.center.y + correction, "o", markersize=10, color=color, alpha=0.6)


def plotBaseFootCenter(axs, jsondata, correction):
    axs.plot(jsondata.combinedCenterX, jsondata.combinedCenterY + correction, "o", markersize=10, color='k', alpha=0.6)
