'''
Created on Sep 14, 2016

@author: localCaleb
'''

import colorsys
from math import sqrt
from Tkinter import tkinter

class Pixel(object):
    '''
    TEST THIS CLASS
    '''

    def __init__(self, red, green, blue):
        '''
        TEST THIS FUNCTION
        '''
        
        self.red = float(red)
        self.green = float(green)
        self.blue = float(blue)
        self.setHSV()
        self.setLab()


    def setHSV(self):
        '''
        TEST THIS FUNCTION
        '''
        hsv = RgbToHsv(self.red, self.green, self.blue)
        self.hue = hsv["Hue"]
        self.saturation = hsv["Saturation"]
        self.value = hsv["Value"]

    def setLab(self):
        '''
        TEST THIS FUNCTION
        '''
        Lab = RGBtoHunterLab(self.red, self.green, self.blue)
        self.L = Lab["L"]
        self.A = Lab["A"]
        self.B= Lab["B"]
        
    def pixelPrint(self):
        return self.L, self.A, self.B
        

def RgbToHsv(R, G, B):
    '''TEST THIS FUNCTION'''
    r = R/255.0
    g = G/255.0
    b = B/255.0
    hsv = colorsys.rgb_to_hsv(r, g, b)
    H = hsv[0]*360
    S = hsv[1]
    V = hsv[2]
    return {"Hue":H, "Saturation":S, "Value":V}

def RgbToXYZ(R, G, B):
    '''TEST THIS FUNCTION'''
    fractionR = R/255.0
    fractionG = G/255.0
    fractionB = B/255.0

    if (fractionR > 0.04045):
        fractionR = ((fractionR + 0.055)/1.055)**2.4
    else:
        fractionR = fractionR/12.92
    if (fractionG > 0.04045):
        fractionG = ((fractionG + 0.055)/1.055)**2.4
    else:
        fractionG = fractionG/12.92
    if (fractionB > 0.04045):
        fractionB = ((fractionB + 0.055)/1.055)**2.4
    else:
        fractionB = fractionB/12.92

    fractionR = fractionR*100
    fractionG = fractionG*100
    fractionB = fractionB*100

    X = fractionR*0.4124 + fractionG*0.3576 + fractionB*.1805
    Y = fractionR*0.2126 + fractionG*0.7152 + fractionB*.0722
    Z = fractionR*0.0193 + fractionG*0.1192 + fractionB*.9505

    return {"X":X, "Y":Y, "Z":Z}

def XyzToHunterLab(X,Y,Z):
    '''TEST THIS FUNCTION'''
    L = 10*sqrt(Y)
    A = 17.5*(((1.02*X)-Y)/sqrt(Y))
    B = 7*((Y-(0.847*Z))/sqrt(Y))

    return {"L":L, "A":A, "B":B}

def RGBtoHunterLab(r,g,b):
    '''
    TEST THIS
    '''
    if (r==0) and (g ==0) and (b == 0):
        return {"L":0, "A":0, "B":0}
    else:
        xyz = RgbToXYZ(r, g, b)
        HLab = XyzToHunterLab(xyz["X"], xyz["Y"], xyz["Z"])
        return HLab
