'''
Created on May 19, 2016

@author: cmhul
'''
from Tkinter import Tk
import csv
import math
import os
import tkFileDialog
import colorsys

from IPython.core.display import Math
import numpy
from scipy import stats

import cProfile


class RepLine(object):
    '''
    This Class holds one Line from one Rep of Corn Cobs, each with  one or more corn cobs, and each corn Cob with one or more Kernel.
     Further, each Kernel has a list of Red, Green, and Blue values for that kernels colors.
    '''

    repDirectory = ''
    accessionName = ''
    numberOfKernels = 0
    colorsMeanOf2StdRange = 0
    hsvMeanOf2StdRange = 0
    cobStatistics = {}

    def __init__(self, startInDirectory = '', name = '', show = False):
        '''
        Ask user for a directory and a Row name, and creates the above mentioned data structure:
        '''
        Tk().withdraw()
        if startInDirectory == '':
            self.repDirectory = str(tkFileDialog.askdirectory())
        else:
            self.repDirectory = startInDirectory
        if name == '':
            self.accessionName = getNameFromPath()
        else:
            self.accessionName = name
        self.cobs = self.setCobs()
        self.kernels = self.setKernelsandRGB()
        self.getAllColorStats(show = show)

    def setCobs(self):
        '''
        Will go through the repDirectory and look for all files that contain the same accessionName as self.accessionName.
        It will then create an empty dict with the key as the filename, and add all those empty dictionaries
        to cobDict and return the cobDict.
        '''
        cobDict = {}
        for file in os.listdir(self.repDirectory):
            if ("_" + self.accessionName + ".") in file:
                fileWithoutLastExt = os.path.splitext(file)[0]
                fileWithoutFirstExt = os.path.splitext(fileWithoutLastExt)[0]
                cobDict[fileWithoutFirstExt] = {}
        return cobDict

    def setKernelsandRGB(self):
        '''
        For each entry in self.cobs, it will open the file with that name in repDirectory.
        The file is a csv file of the format "accessionName, Kernel, R, G, B". This function will return a list of
        ints that correspond to the number of kernels that are associated with the Cob file.
        '''
        progressBar = 0
        for key in self.cobs:
            progressBar += 1
            filePath = self.repDirectory + "/" + key + ".tif.csv"
            with open(filePath) as csvFile:
                csvReader = csv.reader(csvFile)
                csvList = list(csvReader)
                print "Cob: ", progressBar,"/",len(self.cobs)
                pixelNum = 0
                for line in csvList:
                    currentKernel = 0
                    if line[1] != currentKernel and line[1] != '' and line[1] != "Kernel #":
                        currentKernel = int(line[1])
                    if ("Kernel: " + str(currentKernel)) not in self.cobs[key] and line[1] != "Kernel #" and line[1] !='':
                        self.cobs[key]["Kernel: " + line[1]] = {}
                    if line[1] != "Kernel #":
                        try:
                            if line[4] != '':
                                self.cobs[key]["Kernel: " + str(currentKernel)]["Pixel: " + str(pixelNum)] = {"Red":int(line[2]),
                                                                                                              "Green":int(line[3]),
                                                                                                              "Blue":int(line[4])}
                                pixelNum +=1
                        except IndexError:
                            pass

    def getNumberOfCobs(self):
        '''
        returns the number of Cobs in the RepLine Object's cobs dictionary
        '''
        return len(self.cobs.keys())

    def getCob(self, cobNumber):
        '''
        Takes in a Cob number and returns the dictionary of that Cob within the current RepLine objects
        '''
        cob = str(cobNumber) + "_" + self.accessionName
        return self.cobs[cob]

    def getKernel(self,cobNumber, kernelNumber):
        if type(cobNumber) == int and type(kernelNumber) == int:
            return self.getCob(cobNumber)["Kernel: %s" % kernelNumber]
        elif type(cobNumber) == int and type(kernelNumber) == str:
            return self.getCob(cobNumber)[kernelNumber]
        elif type(cobNumber) == str and type(kernelNumber) == int:
            return self.cobs[cobNumber]["Kernel: %s" % kernelNumber]
        elif type(cobNumber) == str and type(kernelNumber) == str:
            return self.cobs[cobNumber][kernelNumber]

    def getKernelColorList(self,cobNumber, kernelNumber, show = False):
        '''
        returns a dictionary contaning the red, green, and blue Pixel lists for the Kernel.
        '''
        kernel = self.getKernel(cobNumber, kernelNumber)
        redValueList = []
        greenValueList = []
        blueValueList = []
        numberOfPixels = len(kernel.keys())
        for key, value in kernel.iteritems():
            if "Max" not in key:
                redValueList.append(value["Red"])
                blueValueList.append(value["Blue"])
                greenValueList.append(value["Green"])
        colorLists = {"Kernel":kernel, "Red":redValueList, "Green":greenValueList,"Blue":blueValueList}
        return colorLists

    def getKernelStatistics(self, cobNumber, kernelNumber, show = False):
        '''
        returns dictionary with the means of the kernels Red, Blue, and Green pixels
        '''
        kernelColorList = self.getKernelColorList(cobNumber, kernelNumber, show)
        kernel = kernelColorList["Kernel"]
        redValueList = kernelColorList["Red"]
        greenValueList = kernelColorList["Green"]
        blueValueList = kernelColorList["Blue"]
        redMean = numpy.array(redValueList).mean()
        greenMean = numpy.array(greenValueList).mean()
        blueMean = numpy.array(blueValueList).mean()
        colorDict = {"Red":redMean, "Green":greenMean, "Blue":blueMean}
        if show == True:
            print colorDict
        return colorDict

    def getCobStatistics(self, cobNumber, show = False):
        '''
        returns color statistics for the Cob:
            Red Mean, Green Mean, Blue Mean
        '''
        listOf2StdMeansRed = []
        listOf2StdMeansGreen = []
        listOf2StdMeansBlue = []
        listOf2StdMeansHue = []
        listOf2StdMeansSaturation = []
        listOf2StdMeansValue = []
        kernelNumber = 1
        cob = self.getCob(cobNumber)
        numberOfKernels = len(cob.keys())
        kernelList = cob.keys()
        while kernelNumber <= numberOfKernels:
            stats = self.getColorStatistics(cobNumber, kernelNumber, show)
            listOf2StdMeansRed.append(stats["RedStatistics"]["2StdMean"])
            listOf2StdMeansGreen.append(stats["GreenStatistics"]["2StdMean"])
            listOf2StdMeansBlue.append(stats["BlueStatistics"]["2StdMean"])
            listOf2StdMeansHue.append(stats["HueStatistics"]["2StdMean"])
            listOf2StdMeansSaturation.append(stats["SaturationStatistics"]["2StdMean"])
            listOf2StdMeansValue.append(stats["ValueStatistics"]["2StdMean"])
            kernelNumber += 1
        meanOf2StdRangeRed = numpy.array(listOf2StdMeansRed).mean()
        meanOf2StdRangeGreen = numpy.array(listOf2StdMeansGreen).mean()
        meanOf2StdRangeBlue = numpy.array(listOf2StdMeansBlue).mean()
        meanOf2StdRangeHue = numpy.array(listOf2StdMeansHue).mean()
        meanOf2StdRangeSaturation = numpy.array(listOf2StdMeansSaturation).mean()
        meanOf2StdRangeValue = numpy.array(listOf2StdMeansValue).mean()
        redDict = {"meanOf2StdRange": meanOf2StdRangeRed}
        greenDict = {"meanOf2StdRange": meanOf2StdRangeGreen}
        blueDict = {"meanOf2StdRange": meanOf2StdRangeBlue}
        hueDict ={"meanOf2StdRange":meanOf2StdRangeHue}
        saturationDict ={"meanOf2StdRange":meanOf2StdRangeSaturation}
        valueDict ={"meanOf2StdRange":meanOf2StdRangeValue}
        return {"Cob": "%s_%s" %(cobNumber, self.accessionName), "kernelsPerCob": numberOfKernels,
                "Red": redDict, "Green": greenDict, "Blue":blueDict, "Hue": hueDict, "Saturation":saturationDict,"Value":valueDict}

    def getColorList(self, cobNumber, kernelNumber, color):
        assert cobNumber-1 in xrange(len(self.cobs.keys()))
        assert color in ["Red","Green","Blue"], "Invalid color: %s" % color
        assert kernelNumber-1 in xrange(len(self.getCob(cobNumber).keys())), "Kernel number not in range"

        colorList = []
        kernel = self.getKernel(cobNumber, kernelNumber)
        maxColorValue = 0
        for key,value in kernel.iteritems():
            if "Max" not in key:
                colorList.append(value[color])
                if value[color] > maxColorValue:
                    maxColorValue = value[color]
        kernel["Max%s"%color] = maxColorValue
        return colorList

    def getHSVList(self, cobNumber, kernelNumber):
        hList = []
        sList = []
        vList = []
        kernel = self.getKernel(cobNumber, kernelNumber)
        maxHue =0
        maxSaturation =0
        maxValue =0
        for key,value in kernel.iteritems():
            if "Max" not in key:
                r = value["Red"]
                g = value["Green"]
                b = value["Blue"]
                hsvDict = RgbToHsv(r, g, b)
                hList.append(hsvDict["Hue"])
                sList.append(hsvDict["Saturation"])
                vList.append(hsvDict["Value"])
                if hsvDict["Hue"] > maxHue:
                    maxHue = hsvDict["Hue"]
                if hsvDict["Saturation"] > maxSaturation:
                    maxSaturation = hsvDict["Saturation"]
                if hsvDict["Value"] > maxValue:
                    maxValue = hsvDict["Value"]
        hsv = {"HueList":hList, "SaturationList":sList, "ValueList":vList,
               "maxHue":maxHue, "maxSaturation":maxSaturation,"maxValue":maxValue}
        return hsv

    def highestFrequency(self, list):
        '''
        inputs a list and returns the value of that list that occurs most frequently.
        '''
        frequencyDict = {}
        maxNum = 0
#
#         for value in list:
#             if value in frequencyDict.keys():
#                 frequencyDict[value] += 1
#             else:
#                 frequencyDict[value] = 1
#             if maxNum == 0:
#                 maxNum = value
#             if frequencyDict[value] > frequencyDict[maxNum]:
#                 maxNum = value
#         return maxNum

        modeNdarray = stats.mode(list)[0]
        modeList = modeNdarray.tolist()
        return modeList[0]

    def getColorStatistics(self,cobNumber, kernelNumber, show = False):
        '''
        Calculates the following stats for all colors of a Kernel:
            mean, mode, maxValue, minValue, standard deviation, mean + 2 SDs, mean - 2SDs, +- 2SD range, mean of +- 2SD range
        '''

        assert cobNumber-1 in xrange(len(self.cobs.keys()))
        assert kernelNumber-1 in xrange(len(self.getCob(cobNumber).keys())), "Kernel number not in range"

        colorListRed = self.getColorList(cobNumber, kernelNumber, "Red")
        colorListGreen = self.getColorList(cobNumber, kernelNumber, "Green")
        colorListBlue = self.getColorList(cobNumber, kernelNumber, "Blue")
        hsvListDict = self.getHSVList(cobNumber, kernelNumber)
        colorListHue = hsvListDict["HueList"]
        colorListSaturation = hsvListDict["SaturationList"]
        colorListValue = hsvListDict["ValueList"]
        modeRed = self.highestFrequency(colorListRed)
        modeGreen = self.highestFrequency(colorListGreen)
        modeBlue = self.highestFrequency(colorListBlue)
        modeHue = self.highestFrequency(colorListHue)
        modeSaturation = self.highestFrequency(colorListSaturation)
        modeValue = self.highestFrequency(colorListValue)
        meanRed = numpy.array(colorListRed).mean()
        meanGreen = numpy.array(colorListGreen).mean()
        meanBlue = numpy.array(colorListBlue).mean()
        meanHue = numpy.array(colorListHue).mean()
        meanSaturation = numpy.array(colorListSaturation).mean()
        meanValue = numpy.array(colorListValue).mean()
        highestValueRed = self.getKernel(cobNumber, kernelNumber)["MaxRed"]
        highestValueGreen = self.getKernel(cobNumber, kernelNumber)["MaxGreen"]
        highestValueBlue = self.getKernel(cobNumber, kernelNumber)["MaxBlue"]
        highestValueHue = hsvListDict["maxHue"]
        highestValueSaturation = hsvListDict["maxSaturation"]
        highestValueValue = hsvListDict["maxValue"]
        lowestValueRed = min(colorListRed)
        lowestValueGreen = min(colorListGreen)
        lowestValueBlue = min(colorListBlue)
        lowestValueHue = min(colorListHue)
        lowestValueSaturation = min(colorListSaturation)
        lowestValueValue = min(colorListValue)
        stdRed = numpy.array(colorListRed).std()
        stdGreen = numpy.array(colorListGreen).std()
        stdBlue = numpy.array(colorListBlue).std()
        stdHue = numpy.array(colorListHue).std()
        stdSaturation = numpy.array(colorListSaturation).std()
        stdValue = numpy.array(colorListValue).std()
        moreTwoStdRed = modeRed + 2*stdRed
        moreTwoStdGreen = modeGreen + 2*stdGreen
        moreTwoStdBlue = modeBlue + 2*stdBlue
        lessTwoStdRed = modeRed - 2*stdRed
        lessTwoStdGreen = modeGreen - 2*stdGreen
        lessTwoStdBlue = modeBlue - 2*stdBlue
        moreTwoStdHue = modeHue + stdHue
        moreTwoStdSaturation = modeSaturation + stdSaturation
        moreTwoStdValue = modeValue + stdValue
        lessTwoStdHue = modeHue - 2*stdHue
        lessTwoStdSaturation = modeSaturation - 2*stdSaturation
        lessTwoStdValue = modeValue - 2*stdValue
        twoStdRangeColorListRed = []
        twoStdRangeColorListGreen = []
        twoStdRangeColorListBlue = []
        twoStdRangeColorListHue = []
        twoStdRangeColorListSaturation = []
        twoStdRangeColorListValue = []
        kernel = self.getKernel(cobNumber, kernelNumber)
        for pixel,colors in kernel.iteritems():
            if "Pixel: " in pixel:
                pixelColorsWithinRGB2StdRange = (colors["Red"] >= lessTwoStdRed and colors["Red"] <= moreTwoStdRed and
                                                 colors["Green"] >= lessTwoStdGreen and colors["Green"] <= moreTwoStdGreen and
                                                 colors["Blue"] >= lessTwoStdBlue and colors["Blue"] <= moreTwoStdBlue)

                hsvDict = RgbToHsv(colors["Red"], colors["Green"], colors["Blue"])
                hue = hsvDict["Hue"]
                saturation = hsvDict["Saturation"]
                value = hsvDict["Value"]
                pixelColorsWithinHSV2StdRange = (hue >= lessTwoStdHue and hue <= moreTwoStdHue and
                                                 saturation >= lessTwoStdSaturation and saturation <= moreTwoStdSaturation and
                                                 value >= lessTwoStdValue and value <= moreTwoStdValue)
                if pixelColorsWithinRGB2StdRange:
                    for color in ["Red","Green","Blue"]:
                        if type(colors[color]) == int:
                            twoStdRangeColorListRed.append(colors["Red"])
                            twoStdRangeColorListGreen.append(colors["Green"])
                            twoStdRangeColorListBlue.append(colors["Blue"])
                if pixelColorsWithinHSV2StdRange:
                    for hsv in [hue,saturation,value]:
                        if type(hsv) == float:
                            twoStdRangeColorListHue.append(hue)
                            twoStdRangeColorListSaturation.append(saturation)
                            twoStdRangeColorListValue.append(value)
        twoStdRangeMeanRed = numpy.array(twoStdRangeColorListRed).mean()
        twoStdRangeMeanGreen = numpy.array(twoStdRangeColorListGreen).mean()
        twoStdRangeMeanBlue = numpy.array(twoStdRangeColorListBlue).mean()
        twoStdRangeMeanHue = numpy.array(twoStdRangeColorListHue).mean()
        twoStdRangeMeanSaturation = numpy.array(twoStdRangeColorListSaturation).mean()
        twoStdRangeMeanValue = numpy.array(twoStdRangeColorListValue).mean()
        redDict =  {"totalMean": meanRed,
                          "mode": modeRed,
                          "std": stdRed,
                          "max": highestValueRed,
                          "min": lowestValueRed,
                          "2StdMean": twoStdRangeMeanRed}
        greenDict = {"totalMean": meanGreen,
                          "mode": modeGreen,
                          "std": stdGreen,
                          "max": highestValueGreen,
                          "min": lowestValueGreen,
                          "2StdMean": twoStdRangeMeanGreen}
        blueDict = {"totalMean": meanBlue,
                          "mode": modeBlue,
                          "std": stdBlue,
                          "max": highestValueBlue,
                          "min": lowestValueBlue,
                          "2StdMean": twoStdRangeMeanBlue}
        hueDict = {"totalMean": meanHue,
                          "mode": modeHue,
                          "std": stdHue,
                          "max": highestValueHue,
                          "min": lowestValueHue,
                          "2StdMean":twoStdRangeMeanHue}
        saturationDict = {"totalMean": meanSaturation,
                          "mode": modeSaturation,
                          "std": stdSaturation,
                          "max": highestValueSaturation,
                          "min": lowestValueSaturation,
                          "2StdMean":twoStdRangeMeanSaturation}
        valueDict = {"totalMean": meanValue,
                          "mode": modeValue,
                          "std": stdValue,
                          "max": highestValueValue,
                          "min": lowestValueValue,
                          "2StdMean":twoStdRangeMeanValue}

        colorStatisticsDict = {"accession": self.accessionName,
                          "Cob": cobNumber,
                          "Kernel": kernelNumber,
                          "RedStatistics":redDict,
                          "GreenStatistics":greenDict,
                          "BlueStatistics":blueDict,
                          "HueStatistics":hueDict,
                          "SaturationStatistics":saturationDict,
                          "ValueStatistics":valueDict}
        if show == True:
            print colorStatisticsDict
        return colorStatisticsDict

    def getAllColorStats(self, show = False):
        '''
        Calculated color statistics for each color on all kernels of a single accession.
        Further Calculates the following for the entire accession:
            total number of kernels, mean of 2SD range values for each color
        '''
        numberOfKernels = 0
        SumOf2StdMeansRed = 0
        SumOf2StdMeansGreen = 0
        SumOf2StdMeansBlue = 0
        SumOf2StdMeansHue = 0
        SumOf2StdMeansSaturation = 0
        SumOf2StdMeansValue = 0
        SumOf2StdMeansHue = 0
        SumOf2StdMeansSaturation = 0
        SumOf2StdMeansValue = 0
        cobNumber = 1
        kernelNumber = 1
        while cobNumber <= len(self.cobs.keys()):
            cobName = "%s_%s" % (cobNumber, self.accessionName)
            if cobName not in self.cobStatistics:
                self.cobStatistics[cobName] = self.getCobStatistics(cobNumber, show)
                stats = self.cobStatistics[cobName]
            else:
                stats = self.getCobStatistics(cobNumber, show)
            SumOf2StdMeansRed += stats["Red"]["meanOf2StdRange"]*stats["kernelsPerCob"]
            SumOf2StdMeansGreen += stats["Green"]["meanOf2StdRange"]*stats["kernelsPerCob"]
            SumOf2StdMeansBlue += stats["Blue"]["meanOf2StdRange"]*stats["kernelsPerCob"]
            SumOf2StdMeansHue +=stats["Hue"]["meanOf2StdRange"]*stats["kernelsPerCob"]
            SumOf2StdMeansSaturation +=stats["Saturation"]["meanOf2StdRange"]*stats["kernelsPerCob"]
            SumOf2StdMeansValue +=stats["Value"]["meanOf2StdRange"]*stats["kernelsPerCob"]
            numberOfKernels += stats["kernelsPerCob"]
            cobNumber +=1
        meanOf2StdRangeRed = SumOf2StdMeansRed/float(numberOfKernels)
        meanOf2StdRangeGreen = SumOf2StdMeansGreen/float(numberOfKernels)
        meanOf2StdRangeBlue = SumOf2StdMeansBlue/float(numberOfKernels)
        meanOf2StdRangeHue = SumOf2StdMeansHue/float(numberOfKernels)
        meanOf2StdRangeSaturation = SumOf2StdMeansSaturation/float(numberOfKernels)
        meanOf2StdRangeValue = SumOf2StdMeansValue/float(numberOfKernels)
        self.colorsMeanOf2StdRange = {"Red": meanOf2StdRangeRed, "Green":meanOf2StdRangeGreen, "Blue":meanOf2StdRangeBlue}
        self.hsvMeanOf2StdRange = {"Hue":meanOf2StdRangeHue, "Saturation":meanOf2StdRangeSaturation, "Value":meanOf2StdRangeValue}
        self.numberOfKernels = numberOfKernels
        print "Done!"

    def getMeanOf2StdRange(self):
        '''
        Returns the mean of all of the 2StdMeans of all the colors of all the kernels of all the cobs.
        '''
        return self.meanOf2StdRange

    def getNumberOfKernels(self):
        '''
        returns total number of kernels in accession.
        '''
        return self.numberOfKernels

def RgbToHsv(R, G, B):
    r = R/255.0
    g = G/255.0
    b = B/255.0
    hsv = colorsys.rgb_to_hsv(r, g, b)
    H = hsv[0]*360
    S = hsv[1]
    V = hsv[2]

    hsvDict = {"Hue":H, "Saturation":S*100, "Value":V*100}
    return hsvDict

def RgbToHsl(R, G, B):
    normR = R/255.0
    normG = G/255.0
    normB = B/255.0
    hsv = colorsys.rgb_to_hls(normR,normG,normB)
    H = hsv[0]*360
    L = hsv[1]
    S = hsv[2]
    hsvDict = {"Hue":H, "Saturation":S*100, "Value":L*100}
    return hsvDict

def getNameFromBasename(basename):
    '''
    Given a basename of form "num_filename" it will return "filename".
    '''
    accessionName = str(basename)
    accessionNameWithoutCobNumber = accessionName[accessionName.index("_")+1:]
    return accessionNameWithoutCobNumber

def getNameFromPath():
    '''
    Given the path to a file of the form "X:/path/to/file/start_filename.ext1.ext2" it will return "filename".
    '''
    accessionName = tkFileDialog.askopenfilename()
    accessionName = os.path.splitext(accessionName)[0]
    '''Repeated intentionally, initial line name has two extensions'''
    accessionName = os.path.splitext(accessionName)[0]
    basename = os.path.basename(accessionName)
    return getNameFromBasename(basename)

def colorStatsForEntireDirectory():
    '''
    Gets the color statistics for all accessions in a folder
    '''
    Tk().withdraw()
    accessionDirectory = str(tkFileDialog.askdirectory())
    accessionList = []
    totalStatsDict = {}
    for file in os.listdir(accessionDirectory):
        if ".tif.csv" in file:
            accessionName = os.path.splitext(file)[0]
            '''Repeated intentionally, initial line name has two extensions'''
            accessionName = os.path.splitext(accessionName)[0]
            accessionName = getNameFromBasename(accessionName)
            if accessionName not in accessionList:
                accessionList.append(accessionName)
    for name in accessionList:
        print "Accession: ",name, accessionList.index(name)+1,"/",len(accessionList)
        Rl = RepLine(Dir = accessionDirectory, name=name)
        totalStatsDict[name] = {"2StdRangeMeansRGB":Rl.colorsMeanOf2StdRange, "2StdRangeMeansHSV":Rl.hsvMeanOf2StdRange}
    newFile = str(accessionDirectory) + "/TotalStats.csv"
    with open(newFile, "w") as file:
        file.write("Accession,2StdRed,2StdGreen,2StdBlue,2StdHue,2StdSat,2StdValue")
        for key in totalStatsDict:
            lineToWrite = "%s,%s,%s,%s,%s,%s,%s," % (key,
                                            totalStatsDict[key]["2StdRangeMeansRGB"]["Red"],
                                            totalStatsDict[key]["2StdRangeMeansRGB"]["Green"],
                                            totalStatsDict[key]["2StdRangeMeansRGB"]["Blue"],
                                            totalStatsDict[key]["2StdRangeMeansHSV"]["Hue"],
                                            totalStatsDict[key]["2StdRangeMeansHSV"]["Saturation"],
                                            totalStatsDict[key]["2StdRangeMeansHSV"]["Value"])
            file.write("\n")
            file.write(lineToWrite)

def testRP(show = False):
    return RepLine(Dir = "..\\..\\..\\..\\College_\\Corn_Color_Phenotyping\\Landrace_Colorimeter_and_Pictures\\Landrace_Photos\\Kernel CSVs",
                   name = "A15LRP0_0003", show = show)

if __name__ == '__main__':
#     print RgbToHsv(100, 23, 74)
#     cProfile.run("RL = testRP()")
    RL = testRP()
#     print "repDirectory: " + RL.repDirectory
#     print "accessionName: " + RL.accessionName
#     print "colors adjusted mean: ", RL.colorsMeanOf2StdRange
#     print "num of kernels: ", RL.numberOfKernels
#     print RL.hsvMeanOf2StdRange
#     cProfile.run("colorStatsForEntireDirectory()", "testDirectory1.cprof")
#     colorStatsForEntireDirectory()
#     end = time.clock()
#     print (timedelta(seconds = (end - start)))
