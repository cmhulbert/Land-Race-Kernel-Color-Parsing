'''
Created on Sep 27, 2016

@author: Caleb Hulbert
'''
from Tkinter import Tk
import colorsys
import csv
import os
import tkFileDialog

import Cob
import Kernel
import Pixel

from sklearn.cluster import KMeans
import numpy as np
from math import ceil, sqrt


class RepLine(object):
    '''
    This Class holds one Line from one Rep of Corn Cobs, each with  one or more corn cobs, and each corn Cob with one or more Kernel.
     Further, each Kernel has a list of Red, Green, and Blue values for that kernels colors.
    '''

    def __init__(self, startInDirectory='', name='', show=False):
        '''
        Ask user for a directory and a Row name, and creates the above mentioned data structure:
        '''
        Tk().withdraw()
        self.repDirectory = ''
        self.accessionName = ''
        self.averageRGB = {"R": 0, "G": 0, "B": 0}
        self.averageLab = {"L": 0, "a": 0, "b": 0}
        self.centers = {"R1": 0, "R2": 0, "G1": 0, "G2": 0, "B1": 0, "B2": 0,
                        "L1": 0, "L2": 0, "a1": 0, "a2": 0, "b1": 0, "b2": 0}
        if startInDirectory == '':
            self.repDirectory = str(tkFileDialog.askdirectory())
            print self.repDirectory
        else:
            self.repDirectory = os.path.abspath(startInDirectory)
        if name == '':
            self.accessionName = str(tkFileDialog.askopenfile(
                initialdir=self.repDirectory).name)[len(self.repDirectory) + 3:-8]
            print self.accessionName
        else:
            self.accessionName = name
            print self.accessionName
        self.cobs = self.setCobs()
        self.setKernelsandRGB(show=show)
        self.clusterMean = [0,0,0]
        self.setColorStats()

    def setCobs(self):
        '''
        Will go through the repDirectory and look for all files that contain the same accessionName as self.accessionName.
        It will then create an empty list with the key as the filename, and add all those empty lists
        to cobDict and return cobDict.
        '''
        print "Setting Cob Dictionary"
        cobDict = {}
        for cobFile in os.listdir(self.repDirectory):
            if ("_" + self.accessionName + ".") in cobFile:
                fileWithoutLastExt = os.path.splitext(cobFile)[0]
                fileWithoutFirstExt = os.path.splitext(fileWithoutLastExt)[0]
                cobDict[fileWithoutFirstExt] = []
        return cobDict

    def setKernelsandRGB(self, show=False):
        '''
        For each entry in self.cobs, it will open the file with that name in repDirectory.
        The file is a csv file of the format "accessionName, Kernel, R, G, B". This function will return a list of
        ints that correspond to the number of kernels that are associated with the Cob file.
        '''
        print "Creating Kernels and Pixels"
        progressBar = 0
        for key in self.cobs:
            progressBar += 1
            kernelList = []
            filePath = self.repDirectory + "/" + key + ".tif.csv"
            with open(filePath) as csvFile:
                csvReader = csv.reader(csvFile)
                csvList = list(csvReader)
                print "Cob: ", progressBar, "/", len(self.cobs)
                listofpixels = []
                currentKernel = 1
                for line in csvList:
                    try:
                        if line[0] == 'Image':
                            pass
                        elif int(line[1]) != currentKernel and line[4] != '':
                            kernelList.append(Kernel.Kernel(listofpixels, name=currentKernel))
                            if show == True:
                                print "Kernel: %s" % currentKernel
                            listofpixels = []
                            currentKernel = int(line[1])
                            currentPixel = Pixel.Pixel(
                                int(line[2]), int(line[3]), int(line[4]))
                            listofpixels.append(currentPixel)
                        elif int(line[1]) == currentKernel:
                            currentPixel = Pixel.Pixel(
                                int(line[2]), int(line[3]), int(line[4]))
                            listofpixels.append(currentPixel)
                    except:
                        IndexError
            self.cobs[key] = Cob.Cob(kernelList)
            print "Kernel's Initialized for %s" % key
        print "All Cob's Initialized"

    def setColorStats(self):
        replineCenters = self.getReplineCenters()
        LMean = 0
        aMean = 0
        bMean = 0
        numberOfCobs = 0
        for cob in self.cobs:
            LMean += self.cobs[cob].averageLab["L"]
            aMean += self.cobs[cob].averageLab["a"]
            bMean += self.cobs[cob].averageLab["b"]
            numberOfCobs += 1
        LMean = LMean / float(numberOfCobs)
        aMean = aMean / float(numberOfCobs)
        bMean = bMean / float(numberOfCobs)
        rgb1 = Kernel.HunterLabToRGB(replineCenters[0][0],
                                     replineCenters[0][1],
                                     replineCenters[0][2])
        rgb2 = Kernel.HunterLabToRGB(replineCenters[1][0],
                                     replineCenters[1][1],
                                     replineCenters[1][2])
        self.averageRGB["R"], self.averageRGB["G"], self.averageRGB[
            "B"] = Kernel.HunterLabToRGB(LMean, aMean, bMean)
        self.averageLab["L"] = LMean
        self.averageLab["a"] = aMean
        self.averageLab["b"] = bMean
        self.centers = {"R1": rgb1["R"], "R2": rgb2["R"], "G1": rgb1["G"], "G2": rgb2["G"], "B1": rgb1["B"], "B2": rgb2["B"],
                        "L1": replineCenters[0][0], "L2": replineCenters[1][0], "a1": replineCenters[0][1], "a2": replineCenters[1][1], "b1": replineCenters[0][2], "b2": replineCenters[1][2]}
        clusterDifference = (abs(replineCenters[0][0] - replineCenters[1][0]) +
                            abs(replineCenters[0][1] - replineCenters[1][1]) +
                            abs(replineCenters[0][2] - replineCenters[1][2]))

    def getCob(self, cobNumber):
        '''
        Takes in a Cob number and returns the dictionary of that Cob within the current RepLine objects
        '''
        cob = str(cobNumber) + "_" + self.accessionName
        return self.cobs[cob]

    def getkernelcolorlists(self, cob, kernel, pixelsPerKernel=100):
        c = self.getCob(cob)
        k = c.kernelList[kernel]
        rgb = k.getrgbTupleList()
        lab = k.getlabTupleList()
        R, G, B, l, a, b = [], [], [], [], [], []
        for x in xrange(len(rgb)):
            if pixelsPerKernel != 0:
                if x % int(ceil((float(len(rgb)) / len(c.kernelList)) / float(pixelsPerKernel))) == 0:
                    R.append(rgb[x][0])
                    G.append(rgb[x][1])
                    B.append(rgb[x][2])
                    l.append(lab[x][0])
                    a.append(lab[x][1])
                    b.append(lab[x][2])
            else:
                R.append(rgb[x][0])
                G.append(rgb[x][1])
                B.append(rgb[x][2])
                l.append(lab[x][0])
                a.append(lab[x][1])
                b.append(lab[x][2])
        return R, G, B, l, a, b

    def getColorListsForAllKernels(self, pixelsPerKernel=0):
        lab = []
        for x in xrange(len(self.cobs.keys())):
            c = self.getCob(x + 1)
            for k in xrange(len(c.kernelList)):
                cobnum = x + 1
                kernelLab = c.kernelList[k].getlabTupleList()
                lab.extend(kernelLab)
        return lab

    def getkernelsaveragecolorlists(self, cob=1):
        R, G, B, l, a, b = [], [], [], [], [], []
        for k in self.getCob(cob).kernelList:
            R.append(k.RgbDict["Mean"]['R'])
            G.append(k.RgbDict["Mean"]['G'])
            B.append(k.RgbDict["Mean"]['B'])
            l.append(k.LabDict['LMean'])
            a.append(k.LabDict['aMean'])
            b.append(k.LabDict['bMean'])
        return R, G, B, l, a, b

    def drawScatterPlot(self, cob=1, kernel=0, pixelsPerKernel=100):
        c = self.getCob(cob)
        k = c.kernelList[kernel]
        r, g, B, l, a, b = self.getkernelcolorlists(
            cob=cob, kernel=kernel, pixelsPerKernel=pixelsPerKernel)
#         return Kernel.showScatterPlot(r,g,B)
        return Kernel.showScatterPlot(l, a, b)

    def drawScatterPlotWithCenters(self, cob=1, kernel=0, pixelsPerKernel=100, x='', y='', z=''):
        if x != '' and y != '' and z != '':
            l = x
            a = y
            b = z
            lab = []
            for i in xrange(len(x)):
                lab.append((x[i], y[i], z[i]))
        else:
            c = self.getCob(cob)
            k = c.kernelList[kernel]
            R, G, B, l, a, b = self.getkernelcolorlists(
                cob=cob, kernel=kernel, pixelsPerKernel=pixelsPerKernel)
            lab = k.getlabTupleList()
        kmeans = KMeans(n_clusters=2).fit(lab).cluster_centers_
        ax = Kernel.showScatterPlot(l, a, b)
        Kernel.addpoints(kmeans, ax, color='r', marker='o')
        return kmeans

    def directoryPrint(self):
        cobs = []
        for cobString in self.cobs.keys():
            cobs.append(self.cobs[cobString].cobPrint())
        return cobs

    def clustersList(self, cob=1):
        clusters = []
        c = self.getCob(cob)
        for k in c.kernelList:
            lab = k.getlabTupleList()
            kmeans = KMeans(n_clusters=2).fit(lab)
            clusters.append(kmeans.cluster_centers_[0])
            clusters.append(kmeans.cluster_centers_[1])
        return np.array(clusters)
        

    def getReplineCenters(self, graph=False, mean=False, size = False):
        kernelcenters = []
        for cob in xrange(len(self.cobs.keys())):
            kernelcenters.extend(self.getCob(cob+1).KernelsCenters)
        KM = KMeans(n_clusters=2, n_init=20).fit(kernelcenters)
        kmeans = KM.cluster_centers_
        if graph == True:
            l, a, b = [], [], []
            for x in kernelcenters:
                l.append(x[0])
                a.append(x[1])
                b.append(x[2])
            ax = Kernel.showScatterPlot(l, a, b)
            Kernel.addpoints(kmeans, ax, color='r', marker='o')
            if mean == True:
                labMean = []
                labMean.append((self.averageLab["L"], self.averageLab["a"],
                                self.averageLab["b"]))
                Kernel.addpoints(labMean, ax, color='g', marker='o')
        if size == True:
            size1 = 0
            size2 = 0
            for x in KM.labels_:
                if x == 0:
                    size1 += 1
                elif x == 1:
                    size2 += 1
            return KM, size1, size2
        return np.array(kmeans)


def RgbToHsv(R, G, B):
    r = R / 255.0
    g = G / 255.0
    b = B / 255.0
    hsv = colorsys.rgb_to_hsv(r, g, b)
    H = hsv[0] * 360
    S = hsv[1]
    V = hsv[2]

    hsvDict = {"Hue": H, "Saturation": S * 100, "Value": V * 100}
    return hsvDict


def RgbToHsl(R, G, B):
    normR = R / 255.0
    normG = G / 255.0
    normB = B / 255.0
    hsv = colorsys.rgb_to_hls(normR, normG, normB)
    H = hsv[0] * 360
    L = hsv[1]
    S = hsv[2]
    hsvDict = {"Hue": H, "Saturation": S * 100, "Value": L * 100}
    return hsvDict


def getNameFromBasename(basename):
    '''
    Given a basename of form "num_filename" it will return "filename".
    '''
    accessionName = str(basename)
    accessionNameWithoutCobNumber = accessionName[
        accessionName.index("_") + 1:]
    return accessionNameWithoutCobNumber


def getNameFromPath(initialdir=''):
    '''
    Given the path to a file of the form "X:/path/to/file/start_filename.ext1.ext2" it will return "filename".
    '''
    if initialdir == '':
        accessionName = tkFileDialog.askopenfilename()
    else:
        accessionName = tkFileDialog.askopenfilename(initialdir=initialdir)
    accessionName = os.path.splitext(accessionName)[0]
    '''Repeated intentionally, initial line name has two extensions'''
    accessionName = os.path.splitext(accessionName)[0]
    basename = os.path.basename(accessionName)
    return getNameFromBasename(basename)


def colorStatsForEntireDirectory(startInDirectory='', show=False):
    '''
    Gets the color statistics for all accessions in a folder
    '''
    Tk().withdraw()
    if startInDirectory == '':
        accessionDirectory = str(tkFileDialog.askdirectory())
    else:
        accessionDirectory = startInDirectory
    accessionList = []
    allRepStats = {}
    for cobFile in os.listdir(accessionDirectory):
        if ".tif.csv" in cobFile:
            accessionName = os.path.splitext(cobFile)[0]
            '''Repeated intentionally, initial line name has two extensions'''
            accessionName = os.path.splitext(accessionName)[0]
            accessionName = getNameFromBasename(accessionName)
            if accessionName not in accessionList:
                accessionList.append(accessionName)
    for name in accessionList:
        print "Accession: ", name, accessionList.index(name) + 1, "/", len(accessionList)
        Rl = RepLine(startInDirectory=accessionDirectory, name=name, show=show)
        kMeans, size1, size2 = Rl.getReplineCenters(size  = True)
        # allRepStats.update({name: Rl.centers})
        del(Rl)
    # return allRepStats
    newFile = str(accessionDirectory) + "/TotalStats.csv"
    with open(newFile, "w") as results:
        results.write(
            "Accession,Red centers,Green centers,Blue centers,Hunter L centers,Hunter a centers,Hunter b centers")
        for key in allRepStats:
            line1 = "%s,%s,%s,%s,%s,%s,%s" % (key,
                                              allRepStats[key]["R1"],
                                              allRepStats[key]["G1"],
                                              allRepStats[key]["B1"],
                                              allRepStats[key]["L1"],
                                              allRepStats[key]["a1"],
                                              allRepStats[key]["b1"],)
            line2 = "%s,%s,%s,%s,%s,%s,%s" % ('',
                                              allRepStats[key]["R2"],
                                              allRepStats[key]["G2"],
                                              allRepStats[key]["B2"],
                                              allRepStats[key]["L2"],
                                              allRepStats[key]["a2"],
                                              allRepStats[key]["b2"])
            results.write("\n")
            results.write(line1)
            results.write("\n")
            results.write(line2)


def testRP(show=False):
    return RepLine(startInDirectory="..\\..\\..\\..\\College_\\Corn_Color_Phenotyping\\Landrace_Colorimeter_and_Pictures\\Kernel CSVs",
                   name="A15LRP0_0003", show=show)


def main(args=0):
    # return RepLine(startInDirectory = "..\\..\\..\\..\\College_\\Corn_Color_Phenotyping\\Landrace_Colorimeter_and_Pictures\\Landrace_Photos\\Kernel CSVs", show = False)
    # return colorStatsForEntireDirectory(startInDirectory = ".\TEST",
    # colorStatsForEntireDirectory(startInDirectory="..\\..\\..\\..\\College_\\Corn_Color_Phenotyping\\Landrace_Colorimeter_and_Pictures\\Landrace_Photos\\Kernel CSVs", show=False)
    # colorStatsForEntireDirectory(startInDirectory = 'C:/Users/cmhul/Google Drive/College_/Corn_Color_Phenotyping/Hybrid_Phenotyping/Kernel CSVs')

    if args == 0:
        r = RepLine(
            startInDirectory='C:/Users/cmhul/Google Drive/College_/Corn_Color_Phenotyping/Hybrid_Phenotyping/Kernel CSVs',
            name='A15LRH0_0007')
    # elif args == 1:
    #     r = RepLine(
    #         startInDirectory='C:/Users/cmhul/Google Drive/College_/Corn_Color_Phenotyping/Hybrid_Phenotyping/Kernel CSVs',
    #         name='A15LRH0_0019')
    #     r.getReplineCenters(graph=True, mean=True)
    # elif args == 2:
    #     r = RepLine(
    #         startInDirectory='C:/Users/cmhul/Google Drive/College_/Corn_Color_Phenotyping/Hybrid_Phenotyping/Kernel CSVs',
    #         name='A15LRH0_0071')
    #     r.getReplineCenters(graph=True, mean=True)

    # c = r.getCob(1)
    # k1 = []
    # k2 = []
    # Mean1 = c.meanOfKernelList(k1)
    # kMeans = r.getReplineCenters()
    # c1 = r.getCob(1)
    # for k in c1.kernelList:
    #     print k.RgbDict["Mean"]
    return r# , Mean1, kMeans

if __name__ == '__main__':
    main()
