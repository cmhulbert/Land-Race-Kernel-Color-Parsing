'''
Created on Sep 14, 2016

@author: localCaleb
'''
from math import sqrt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import Pixel
from sklearn.cluster import KMeans


class Kernel(object):
    '''
    A single kernel of corn. Contains a list of Pixels, along with statistics done on those pixels
    '''

    def __init__(self, pixelList, name):
        '''
        Adds a list of pixels to the Kernel object, as well as calculating statistics
        TEST ALL OF THIS
        '''
        self.name = ''
        self.pixelList = []
        self.numberOfPixels = 0
        self.RgbDict = {"Mean": '', "Mode": '', "2SDmean": ''}
        self.LabDict = {"LMean": '', "LMode": '', "L2SDMean": '', "LSD": '',
                        "aMean": '', "aMode": '', "a2SDMean": '', "aSD": '',
                        "bMean": '', "bMode": '', "b2SDMean": '', "bSD": ''}
        self.centers = []
        self.pointsPerCluster0 = 0
        self.pointsPerCluster1 = 0
        self.plot = 0
        self.name = name
        LList = []
        aList = []
        bList = []
        frequencyDict = {}
        self.pixelList = pixelList
        self.numberOfPixels = len(self.pixelList)
        for pixel in self.pixelList:
            LList.append(pixel.L)
            aList.append(pixel.A)
            bList.append(pixel.B)

            color = "r%s,g%s,b%s" % (pixel.red, pixel.green, pixel.blue)
            if color in frequencyDict.keys():
                frequencyDict[color] += 1
            else:
                frequencyDict[color] = 1
        mode = max(frequencyDict, key=frequencyDict.get)
        self.RgbDict["Mode"] = mode
        r = float(mode[1:mode.index("g") - 1])
        g = float(mode[mode.index("g") + 1:mode.index("b") - 1])
        b = float(mode[mode.index("b") + 1:])
        lab = Pixel.RGBtoHunterLab(r, g, b)
        self.LabDict["LMode"] = lab["L"]
        self.LabDict["aMode"] = lab["A"]
        self.LabDict["bMode"] = lab["B"]
        LMeanSD = meanstdv(LList)
        aMeanSD = meanstdv(aList)
        bMeanSD = meanstdv(bList)
        LMean = float(LMeanSD[0])
        aMean = float(aMeanSD[0])
        bMean = float(bMeanSD[0])
        LSD = float(LMeanSD[1])
        aSD = float(aMeanSD[1])
        bSD = float(bMeanSD[1])
        self.LabDict["LMean"] = LMean
        self.LabDict["aMean"] = aMean
        self.LabDict["bMean"] = bMean
        self.LabDict["LSD"] = LSD
        self.LabDict["aSD"] = aSD
        self.LabDict["bSD"] = bSD
        self.RgbDict["Mean"] = HunterLabToRGB(self.LabDict["LMean"], self.LabDict[
                                              "aMean"], self.LabDict["bMean"])
        L2SDSum = 0
        L2SDCount = 0
        a2SDSum = 0
        a2SDCount = 0
        b2SDSum = 0
        b2SDCount = 0
        for L in LList:
            if (L <= (LMean + (2 * LSD))) and (L >= (LMean - (2 * LSD))):
                L2SDSum += L
                L2SDCount += 1
        for a in aList:
            if (a <= (aMean + (2 * aSD))) and (a >= (aMean - (2 * aSD))):
                a2SDSum += a
                a2SDCount += 1
        for b in bList:
            if (b <= (bMean + (2 * bSD))) and (b >= (bMean - (2 * bSD))):
                b2SDSum += b
                b2SDCount += 1
        self.LabDict["L2SDMean"] = L2SDSum / L2SDCount
        self.LabDict["a2SDMean"] = a2SDSum / a2SDCount
        self.LabDict["b2SDMean"] = b2SDSum / b2SDCount
        # del self.pixelList[:]
        self.setCenters()

    def getrgbTupleList(self):
        rgbTupleList = []
        for pixel in self.pixelList:
            rgbTupleList.append([pixel.red, pixel.green, pixel.blue])
        return rgbTupleList

    def getlabTupleList(self):
        labTupleList = []
        for pixel in self.pixelList:
            labTupleList.append([pixel.L, pixel.A, pixel.B])
        return labTupleList

    def kernelPrint(self):
        pixels = [] = []
        for p in self.pixelList:
            pixels.append(p.pixelPrint())
        return pixels

    def SdDistance(self):
        return self.LabDict["LSD"] + self.LabDict["aSD"] + self.LabDict["bSD"]

    def setCenters(self):
        lab = self.getlabTupleList()
        km = KMeans(n_clusters=2).fit(lab)
        self.pointsPerCluster0 = 0
        self.pointsPerCluster1 = 0
        for x in km.labels_:
            if x == 0:
                self.pointsPerCluster0 += 1
            elif x == 1:
                self.pointsPerCluster1 += 1
        largestClusterSize = max(
            self.pointsPerCluster0, self.pointsPerCluster1)
        smallestClusterSize = min(
            self.pointsPerCluster0, self.pointsPerCluster1)
        prcntLarger = float(largestClusterSize) / float(smallestClusterSize)
        print self.name, prcntLarger
        if prcntLarger > 1.7:
            self.centers.append([self.LabDict["LMean"],
                                 self.LabDict["aMean"],
                                 self.LabDict["bMean"]])
            self.centers.append([self.LabDict["LMean"],
                                 self.LabDict["aMean"],
                                 self.LabDict["bMean"]])
        else:
            self.centers.append(km.cluster_centers_[0])
            self.centers.append(km.cluster_centers_[1])


def showScatterPlot(x, y, z, color='b', marker='.', xlabel='L', ylabel='a', zlabel='b'):
    plot = plt.figure()
    plt.close(1)
    del(plot)
    plot = plt.figure()
    ax = plot.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c=color, marker=marker)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    plt.ion()
    plt.show()
    return ax


def addpoints(listofpoints, axes, color='b', marker=','):
    x, y, z = [], [], []
    for xyz in listofpoints:
        x.append(xyz[0])
        y.append(xyz[1])
        z.append(xyz[2])
    axes.scatter(x, y, z, color=color, marker=marker)


def meanstdv(inputList):
    try:
        std = []
        Listlen = float(len(inputList))
        mean = (sum(inputList) / Listlen)
        SDsum = 0
        for value in inputList:
            SDsum += pow((value - mean), 2)
        stddev = sqrt(SDsum / Listlen)
        return [float(mean), float(stddev)]
    except:
        print "does not compute"
        return "na", "na"


def HunterLabToXYZ(L, a, b):
    '''
    TESTED
    '''
    tempY = L / 10.0
    tempX = (a / 17.5) * (L / 10.0)
    tempZ = (b / 7.0) * (L / 10.0)

    Y = tempY ** 2
    X = (tempX + Y) / 1.02
    Z = (-1) * (tempZ - Y) / 0.847

    return {"X": X, "Y": Y, "Z": Z}


def XYZToRGB(X, Y, Z):
    '''
    TESTED
    '''
    tempX = X / 100.0
    tempY = Y / 100.0
    tempZ = Z / 100.0

    tempR = (tempX * 3.2406) + (tempY * -1.5372) + (tempZ * -0.4986)
    tempG = (tempX * -0.9689) + (tempY * 1.8758) + (tempZ * 0.0415)
    tempB = (tempX * 0.0557) + (tempY * -0.2040) + (tempZ * 1.0570)

    if (tempR > 0.0031308):
        tempR = 1.055 * (tempR ** (1 / 2.4)) - 0.055
    else:
        tempR = 12.92 * tempR
    if (tempG > 0.0031308):
        tempG = 1.055 * (tempG ** (1 / 2.4)) - 0.055
    else:
        tempG = 12.92 * tempG
    if (tempB > 0.0031308):
        tempB = 1.055 * (tempB ** (1 / 2.4)) - 0.055
    else:
        tempB = 12.92 * tempB

    R = tempR * 255
    G = tempG * 255
    B = tempB * 255

    return {"R": R, "G": G, "B": B}


def HunterLabToRGB(L, a, b):
    '''
    TESTED
    '''
    xyz = HunterLabToXYZ(L, a, b)
    rgb = XYZToRGB(xyz["X"], xyz["Y"], xyz["Z"])

    return rgb


def main():
    pl = []
    p1 = Pixel.Pixel(0, 0, 0)
    p2 = Pixel.Pixel(0, 0, 0)
    p3 = Pixel.Pixel(0, 0, 0)
    p4 = Pixel.Pixel(31, 57, 219)
    p5 = Pixel.Pixel(31, 57, 219)
    p6 = Pixel.Pixel(31, 57, 219)
    p7 = Pixel.Pixel(0, 0, 0)
    p8 = Pixel.Pixel(0, 0, 0)
    p9 = Pixel.Pixel(0, 0, 0)
    p10 = Pixel.Pixel(255, 255, 255)
    pl.extend([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10])
    k = Kernel(pl)
    print k.__dict__
    return k

if __name__ == "__main__":
    main()
