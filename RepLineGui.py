'''
Created on May 20, 2016

@author: cmhul
'''

from Tkinter import Tk, Button, Entry, Label, StringVar, OptionMenu, Grid, \
    Listbox, Scrollbar
import os
import tkFileDialog
from ttk import Frame

import RepLine


class RepLineGui(Frame):
    '''
    classdocs
    '''
    lightRed = '#%02x%02x%02x' % (248,203,173)
    lightGreen = '#%02x%02x%02x' % (198,224,180)
    lightBlue = '#%02x%02x%02x' % (155,194,230)
    widgetDict = {}
    RepLine = ''
    accessionList = []
    cobList = []
    activeCob = ''
    kernelList = []
    activeKernel = ''
    pixelList = []
    activePixel = ''
    repDirectory = ''
    accession = ''

    def __init__(self, parent, startInDirectory = ''):
        Frame.__init__(self, parent)
         
        self.parent = parent
        
        self.repDirectory = startInDirectory
        
        self.initUI()
        
    def setAccessionList(self, kwargs):
        if self.repDirectory == '':
            self.repDirectory = str(tkFileDialog.askdirectory())
        self.accessionList = ["Pick Accession"]
        for file in os.listdir(self.repDirectory):
            if ".tif.csv" in file:
                lineName = os.path.splitext(file)[0]
                '''Repeated intentionally, initial line name has two extensions'''
                lineName = os.path.splitext(lineName)[0]
                accessionName = RepLine.getNameFromBasename(lineName)
                if accessionName not in self.accessionList:
                    self.accessionList.append(accessionName)
        pathLabel = self.widgetDict["pathLabel"]
        pathLabel.config(text = "Path: %s" % self.repDirectory)
        
        accessionVar = StringVar()
        accessionMenu = apply(OptionMenu, (self,accessionVar) + tuple(self.accessionList))
        accessionVar.set(self.accessionList[0])
        accessionMenu.grid(row = 1, column=1, sticky= "nsew")
        accessionVar.trace("w", self.setRepLine)
        self.widgetDict["accessionMenu"] = accessionMenu
        self.widgetDict["accessionVar"] = accessionVar

    def setRepLine(self, *args):
        self.accession = self.widgetDict["accessionVar"].get()
        self.widgetDict["accessionLabel"].config(text = "Accession: Loading...        ")
        self.widgetDict["accessionLabel"].update_idletasks()
        self.RepLine = RepLine.RepLine(Dir = self.repDirectory, name= self.accession)
        self.widgetDict["accessionLabel"].config(text = "Accession: %s" % self.accession)
        self.setCobList()
        self.setAccessionStats()
        
    def setCobList(self):
        self.cobList = []
        for cob in xrange(len(self.RepLine.cobs.keys())):
            self.cobList.append(str(cob+1) + "_" + self.RepLine.accessionName)
        if "cobListbox" in self.widgetDict.keys():
            cobListbox = self.widgetDict["cobListbox"]
            cobListbox.delete(0, "end")
            self.widgetDict["cobsLabel"].config(text = "Cobs: %s" % len(self.cobList))
        else:
            cobListbox = Listbox(self)
            self.widgetDict["cobListbox"] = cobListbox
            scrollbar = Scrollbar(cobListbox, orient="vertical")
            cobListbox.config(yscrollcommand = scrollbar.set)
            scrollbar.config(command = cobListbox.yview)
            self.widgetDict["cobsLabel"].config(text = "Cobs: %s" % len(self.cobList))
            cobListbox.grid(row = 3, column = 0, rowspan = 3, sticky = "nsew")
            cobListbox.columnconfigure(0, weight = 1)
            cobListbox.bind("<<ListboxSelect>>", self.updateActiveCob)
            scrollbar.grid(column = 0, sticky = "e")
        for cob in self.cobList:
            cobListbox.insert(self.cobList.index(cob), cob)
        
        
    def updateActiveCob(self, kwarg):
        self.activeCob = self.widgetDict["cobListbox"].get("active")
        self.setKernelList()
        self.setCobStats()
        
    def setKernelList(self):
        self.kernelList = []
        for i in xrange(len(self.RepLine.cobs[self.activeCob])):
            self.kernelList.append("Kernel: " + str(i+1))
        if "kernelListbox" in self.widgetDict.keys():
            kernelListbox = self.widgetDict["kernelListbox"]
            kernelListbox.delete(0, "end")
            self.widgetDict["kernelsLabel"].config(text = "Kernels: %s" % len(self.kernelList))
        else:
            kernelListbox = Listbox(self)
            self.widgetDict["kernelListbox"] = kernelListbox
            scrollbar = Scrollbar(kernelListbox, orient="vertical")
            kernelListbox.config(yscrollcommand = scrollbar.set)
            scrollbar.config(command = kernelListbox.yview)
            self.widgetDict["kernelsLabel"].config(text = "Kernels: %s" % len(self.kernelList))
            kernelListbox.grid(row  = 3, column = 1, rowspan = 3, sticky = "nsew")
            kernelListbox.columnconfigure(0, weight = 1)
            kernelListbox.bind("<<ListboxSelect>>", self.updateActiveKernel)
            scrollbar.grid(column = 1, sticky = "e")
        for kernel in self.kernelList:
            kernelListbox.insert(self.kernelList.index(kernel),kernel)
            
    def updateActiveKernel(self, kwarg):
        self.activeKernel = self.widgetDict["kernelListbox"].get("active")
        self.setPixelList()
        self.setKernelStats()
        
    def setPixelList(self):
        if "pixelListBox" in self.widgetDict.keys():
            pixelListBox = self.widgetDict["pixelListBox"]
            pixelListBox.delete(0, "end")
            self.widgetDict["kernelListbox"].config(text = "Pixels: %s" % len(self.RepLine.getKernel(self.activeCob, self.activeKernel).keys()))
        else:
            pixelListbox = Listbox(self)
            self.widgetDict["pixelListbox"] = pixelListbox
            scrollbar = Scrollbar(pixelListbox, orient="vertical")
            pixelListbox.config(yscrollcommand = scrollbar.set)
            scrollbar.config(command = pixelListbox.yview)
            self.widgetDict["pixelsLabel"].config(text = "Pixels: %s" % len(self.RepLine.getKernel(self.activeCob, self.activeKernel).keys()))
            pixelListbox.grid(row  = 3, column = 2, rowspan = 3, sticky = "nsew")
            pixelListbox.columnconfigure(0, weight = 1)
            pixelListbox.bind("<<ListboxSelect>>", self.updateActivePixel)
            scrollbar.grid(column = 2, sticky = "e")
        cobNumber = self.activeCob[:self.activeCob.index("_")]
        kernelNumber = self.activeKernel[self.activeKernel.index(" ")+1:]
        kernel = self.RepLine.getKernel(int(cobNumber), int(kernelNumber))
        for pixelNumber in xrange(len(kernel.keys())):
            pixelListbox.insert(pixelNumber,"Pixel: %s" % pixelNumber)
            
    def updateActivePixel(self, kwarg):
        self.activePixel = self.widgetDict["pixelListbox"].get("active")
        self.setPixelRGB()
        
    def setPixelRGB(self):
        pixelNumber = int(self.activePixel[self.activePixel.index(" "):])
        redValue = self.RepLine.cobs[self.activeCob][self.activeKernel]["Pixel: %s" %pixelNumber]["Red"]
        greenValue = self.RepLine.cobs[self.activeCob][self.activeKernel]["Pixel: %s" %pixelNumber]["Green"]
        blueValue = self.RepLine.cobs[self.activeCob][self.activeKernel]["Pixel: %s" %pixelNumber]["Blue"]
        if "blueLabel" in self.widgetDict.keys():
            self.widgetDict["redLabel"].config(text = "Red: %s" % redValue, justify = "left")
            self.widgetDict["greenLabel"].config(text = "Green: %s" % greenValue)
            self.widgetDict["blueLabel"].config(text = "Blue: %s"% blueValue)
            pixelAverageColorFill = self.widgetDict["pixelAverageColorFill"]
            averageColor = '#%02x%02x%02x' % (redValue,greenValue,blueValue)
            pixelAverageColorFill = Label(self, bg =averageColor,fg = averageColor,
                                           activebackground = averageColor,
                                           activeforeground = averageColor)
            pixelAverageColorFill.grid(row = 6, column = 3, sticky = "nsew")
        else:
            redLabel = Label(self, text = "Red: %s" % redValue, bg = self.lightRed)
            redLabel.grid(row = 3, column = 3, sticky = "we")
            greenLabel = Label(self, text = "Green: %s" % greenValue, bg = self.lightGreen)
            greenLabel.grid(row = 4, column = 3, sticky = "we")
            blueLabel = Label(self, text = "Blue: %s"% blueValue, bg = self.lightBlue)
            blueLabel.grid(row = 5, column = 3, sticky = "we")
            self.widgetDict["redLabel"] = redLabel
            self.widgetDict["greenLabel"] = greenLabel
            self.widgetDict["blueLabel"] = blueLabel
            averageColor = '#%02x%02x%02x' % (redValue,greenValue,blueValue)
            pixelAverageColorFill = Label(self, bg =averageColor,fg = averageColor,
                                           activebackground = averageColor,
                                           activeforeground = averageColor)
            pixelAverageColorFill.grid(row = 6, column = 3, sticky = "nsew")
            self.widgetDict["pixelAverageColorFill"] = pixelAverageColorFill
            
            
    def setAccessionStats(self):
        accessionStatisticsLabel = Label(self, text = "Accession Statistics: %s" % self.accession, font = "bold")
        accessionStatisticsLabel.grid(row = 6, column = 0, sticky = "w")
        accessionTotalNumberOfKernelsLabel = Label(self,text = "   Total number of Kernels: %s" % self.RepLine.numberOfKernels)
        accessionTotalNumberOfKernelsLabel.grid(row = 7, column = 0)
        accessionRedTopLabel = Label(self, text = "   Red", bg = self.lightRed)
        accessionRedTopLabel.grid(row = 8, column = 0, sticky = "nsew")
        accessionRedMean = Label(self, text = "      2Std Range Mean: %s   " % self.RepLine.colorsMeanOf2StdRange["Red"], bg = self.lightRed)
        accessionRedMean.grid(row = 9, column = 0, sticky = "nsew")
        accessionGreenTopLabel = Label(self, text = "   Green", bg = self.lightGreen)
        accessionGreenTopLabel.grid(row = 8, column = 1, sticky = "nsew")
        accessionGreenMean = Label(self, text = "      2Std Range Mean: %s   " % self.RepLine.colorsMeanOf2StdRange["Green"], bg = self.lightGreen)
        accessionGreenMean.grid(row = 9, column = 1, sticky = "nsew")
        accessionBlueTopLabel = Label(self, text = "   Blue", bg = self.lightBlue)
        accessionBlueTopLabel.grid(row = 8, column = 2, sticky = "nsew")
        accessionBlueMean = Label(self, text = "      2Std Range Mean: %s   " % self.RepLine.colorsMeanOf2StdRange["Blue"], bg = self.lightBlue)
        accessionBlueMean.grid(row = 9, column = 2, sticky = "nsew")
        accessionAverageColorLabel = Label(self, text = "2StdMean Accession Color:")
        accessionAverageColorLabel.grid(row = 7, column = 1, sticky = "e")
        averageColor = '#%02x%02x%02x' % (self.RepLine.colorsMeanOf2StdRange["Red"],
                                          self.RepLine.colorsMeanOf2StdRange["Green"],
                                          self.RepLine.colorsMeanOf2StdRange["Blue"])
        accessionAverageColorFill = Label(self, bg =averageColor,fg = averageColor,
                                           activebackground = averageColor,
                                           activeforeground = averageColor)
        accessionAverageColorFill.grid(row = 7, column = 2, sticky = "nsew")
        
    def setCobStats(self):
        cobStatisticsLabel = Label(self,text = "Cob Statistics: %s" % self.activeCob, font = "bold")
        cobStatisticsLabel.grid(row=10, column = 0, sticky = "w")
        cobRedTopLabel = Label(self, text = "Red:", bg = self.lightRed)
        cobRedTopLabel.grid(row = 11, column = 0, sticky = "nsew")
        cobRedMean = Label(self, text = "2SD Range Mean: %s   " % self.RepLine.cobStatistics[self.activeCob]["Red"]["meanOf2StdRange"], bg = self.lightRed)
        cobRedMean.grid(row = 12, column = 0, sticky = "nsew")
        cobGreenTopLabel = Label(self, text = "Green:", bg = self.lightGreen)
        cobGreenTopLabel.grid(row = 11, column = 1, sticky = "nsew")
        cobGreenMean = Label(self, text = "2SD Range Mean: %s   " % self.RepLine.cobStatistics[self.activeCob]["Green"]["meanOf2StdRange"], bg = self.lightGreen)
        cobGreenMean.grid(row = 12, column = 1, sticky = "nsew")
        cobBlueTopLabel = Label(self, text = "Blue:", bg = self.lightBlue)
        cobBlueTopLabel.grid(row = 11, column = 2, sticky = "nsew")
        cobBlueMean = Label(self, text = "2SD Range Mean: %s   " % self.RepLine.cobStatistics[self.activeCob]["Blue"]["meanOf2StdRange"], bg = self.lightBlue)
        cobBlueMean.grid(row = 12, column = 2, sticky = "nsew")
        cobAverageColorLabel = Label(self, text = "2SD Mean Cob Color:")
        cobAverageColorLabel.grid(row = 10, column = 1, sticky = "e")
        averageColor = '#%02x%02x%02x' % (self.RepLine.cobStatistics[self.activeCob]["Red"]["meanOf2StdRange"],
                                          self.RepLine.cobStatistics[self.activeCob]["Green"]["meanOf2StdRange"],
                                          self.RepLine.cobStatistics[self.activeCob]["Blue"]["meanOf2StdRange"])
        cobAverageColorFill = Label(self, bg =averageColor,fg = averageColor,
                                           activebackground = averageColor,
                                           activeforeground = averageColor)
        cobAverageColorFill.grid(row = 10, column = 2, sticky = "nsew")
        
    def setKernelStats(self):
        cobNumber = int(self.activeCob[:self.activeCob.index("_")])
        kernelNumber = int(self.activeKernel[self.activeKernel.index(" "):])
        colorDict = self.RepLine.getColorStatistics(cobNumber, kernelNumber)
        statsDictRed = colorDict["RedStatistics"]
        statsDictGreen = colorDict["GreenStatistics"]
        statsDictBlue = colorDict["BlueStatistics"]
        kernelStatsLabel = Label(self, text = "Kernel Statistics: %s" % self.activeKernel, font = "bold")
        kernelStatsLabel.grid(row = 13, column = 0, sticky = "w")
        kernelRedTopLabel = Label(self, text = "   Red:", bg = self.lightRed)
        kernelRedTopLabel.grid(row = 14, column = 0, sticky = "nsew")
        kernelRedMean = Label(self, text = "      2Std Range Mean: %s   " % statsDictRed["2StdMean"], bg = self.lightRed)
        kernelRedMean.grid(row = 15, column = 0, sticky = "nsew")
        kernelRedMode = Label(self, text = "      Mode: %s   " % statsDictRed["mode"], bg = self.lightRed)
        kernelRedMode.grid(row = 16, column = 0, sticky = "nsew")
        kernelRedStd = Label(self, text = "      SD: %s   " % statsDictRed["std"], bg = self.lightRed)
        kernelRedStd.grid(row = 17, column = 0, sticky = "nsew")
        kernelGreenTopLabel = Label(self, text = "   Green:", bg = self.lightGreen)
        kernelGreenTopLabel.grid(row = 14, column = 1, sticky = "nsew")
        kernelGreenMean = Label(self, text = "      2Std Range Mean: %s   " % statsDictGreen["2StdMean"], bg = self.lightGreen)
        kernelGreenMean.grid(row = 15, column = 1, sticky = "nsew")
        kernelGreenMode = Label(self, text = "      Mode: %s   " % statsDictGreen["mode"], bg = self.lightGreen)
        kernelGreenMode.grid(row = 16, column = 1, sticky = "nsew")
        kernelGreenStd = Label(self, text = "      SD: %s   " % statsDictGreen["std"], bg = self.lightGreen)
        kernelGreenStd.grid(row = 17, column = 1, sticky = "nsew") 
        kernelBlueTopLabel = Label(self, text = "   Blue:", bg = self.lightBlue)
        kernelBlueTopLabel.grid(row = 14, column = 2, sticky = "nsew")
        kernelBlueMean = Label(self, text = "      2Std Range Mean: %s   " % statsDictBlue["2StdMean"], bg = self.lightBlue)
        kernelBlueMean.grid(row = 15, column = 2, sticky = "nsew")
        kernelBlueMode = Label(self, text = "      Mode: %s   " % statsDictBlue["mode"], bg = self.lightBlue)
        kernelBlueMode.grid(row = 16, column = 2, sticky = "nsew")
        kernelBlueStd = Label(self, text = "      SD: %s   " % statsDictBlue["std"], bg = self.lightBlue)
        kernelBlueStd.grid(row = 17, column = 2, sticky = "nsew")
        kernelAverageColorLabel = Label(self, text = "2StdMean Kernel Color:")
        kernelAverageColorLabel.grid(row = 13, column = 1, sticky = "e")
        averageColor = '#%02x%02x%02x' % (statsDictRed["2StdMean"],
                                          statsDictGreen["2StdMean"],
                                          statsDictBlue["2StdMean"])
        kernelAverageColorFill = Label(self, bg =averageColor,fg = averageColor,
                                           activebackground = averageColor,
                                           activeforeground = averageColor)
        kernelAverageColorFill.grid(row = 13, column = 2, sticky = "nsew")
            
    def testFunction(self, kwargs):
        print self.widgetDict["cobListbox"].get("active")
    
    def testButton(self):
        test = Button(self, text = "test")
        test.grid(row = 1, column = 3, sticky = "nsew")
        test.bind("<ButtonRelease-1>", self.testFunction)
    
    def initUI(self):
        self.parent.title("RepLineGui")    
        
        pathLabel = Label(self, text = "Path: %s" % '')
        pathLabel.grid(row = 0, column = 0, columnspan = 3, sticky = "w")
        self.widgetDict["pathLabel"] = pathLabel
        browseButton = Button(self, text = "Browse")
        browseButton.grid(row = 0, column = 3, sticky = "nsew")
        browseButton.bind("<ButtonRelease-1>", self.setAccessionList)
        self.widgetDict["browseButton"] = browseButton
        accessionLabel = Label(self, text = "Accession:")
        accessionLabel.grid(row = 1, column = 0, sticky = "w")
        self.widgetDict["accessionLabel"] = accessionLabel
        cobsLabel = Label(self, text = "Cobs: Select an Accession" )
        cobsLabel.grid(row = 2, column = 0, sticky = "w")
        self.widgetDict["cobsLabel"] = cobsLabel
        kernelsLabel = Label(self, text = "Kernels: Select a Cob")
        kernelsLabel.grid(row = 2, column = 1, sticky = "w")
        self.widgetDict["kernelsLabel"] = kernelsLabel
        pixelsLabel = Label(self, text = "Pixels: Select a Kernel")
        pixelsLabel.grid(row = 2, column = 2, sticky = "w")
        self.widgetDict["pixelsLabel"] = pixelsLabel
        self.testButton()
        self.pack()
    
def main():  
    root = Tk()
#     root.resizable(0,0)
    Dir =  "..\\..\\..\\..\\College_\\Corn_Color_Phenotyping\\Landrace_Colorimeter_and_Pictures\\Landrace_Photos\\Kernel CSVs" 
    app = RepLineGui(root, Dir = Dir)
    root.mainloop()
    
 


if __name__ == '__main__':
    main()
        