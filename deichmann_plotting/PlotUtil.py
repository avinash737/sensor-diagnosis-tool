def getClusterColor(type):
    if type == 'center':
        return 'y'
    if type == 'bale':
        return 'b'
    if type == 'heel':
        return 'g'
    if type == 'toe':
        return 'r'


def plotHorizontalIndicator(axs):
    for i in range(0, 160):
        if (i % 10 == 0):
            x = [i, i]
            y = [351, 349]
            axs.plot(x, y, "k-")
        elif (i % 5 == 0):
            x = [i, i]
            y = [351, 350]
            axs.plot(x, y, "k-")


def plotVerticalIndicator(axs, start):
    for i in range(start, 0, -1):
        if ((start - i) % 10 == 0):
            x = [160, 150]
            y = [i, i]
            axs.plot(x, y, "k-")
        elif ((start - i) % 5 == 0):
            x = [160, 155]
            y = [i, i]
            axs.plot(x, y, "k-")
