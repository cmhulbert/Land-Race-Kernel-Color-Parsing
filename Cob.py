'''
Created on Sep 14, 2016

@author: localCaleb
'''

import Kernel


class Cob(object):
    '''
    TEST THIS
    '''

    def __init__(self, kernels, show=False):
        '''
        TEST THIS
        '''
        self.name = ''
        self.averageRGB = {"R": 0, "G": 0, "B": 0}
        self.averageLab = {"L": 0, "a": 0, "b": 0}
        self.kernelList = kernels
        self.numberOfKernels = len(self.kernelList)
        LMean = 0
        aMean = 0
        bMean = 0
        #The below code will calculate the 2SDMean wrong!
        for kernel in self.kernelList:
            LMean += kernel.LabDict["L2SDMean"]
            aMean += kernel.LabDict["a2SDMean"]
            bMean += kernel.LabDict["b2SDMean"]
        LMean = LMean / float(self.numberOfKernels)
        aMean = aMean / float(self.numberOfKernels)
        bMean = bMean / float(self.numberOfKernels)
        # the above code is wrong!
        rgb = Kernel.HunterLabToRGB(LMean, aMean, bMean)
        self.averageRGB["R"] = rgb["R"]
        self.averageRGB["G"] = rgb["G"]
        self.averageRGB["B"] = rgb["B"]
        self.averageLab["L"] = LMean
        self.averageLab["a"] = aMean
        self.averageLab["b"] = bMean
        self.KernelsCenters = []
        self.setKernelsCenters()

    def cobPrint(self):
        kernels = []
        for k in self.kernelList:
            kernels.append(k.kernelPrint())
        return kernels

    def meanOfKernelList(self, kernels):
        LMean = 0
        aMean = 0
        bMean = 0
        num = float(len(kernels))
        for index in kernels:
            labdict = self.kernelList[index - 1].LabDict
            LMean += labdict["LMean"]
            aMean += labdict["aMean"]
            bMean += labdict["bMean"]
        LMean = LMean / num
        aMean = aMean / num
        bMean = bMean / num
        return (LMean, aMean, bMean)

    def averageKernelSdDistance(self):
        distance = 0
        for x in self.kernelList:
            distance += x.SdDistance()
        return distance / float(self.numberOfKernels)

    def setKernelsCenters(self):
        for x in self.kernelList:
            self.KernelsCenters.append(x.centers[0])
            self.KernelsCenters.append(x.centers[1])
