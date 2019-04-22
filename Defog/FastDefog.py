from Image import Image
import numpy as np
from multiprocessing import Pool


def oneDFromTwoD(x, y, cols):
    return x*cols+y

def flatten(arr):
    output = []
    rows = len(arr)
    cols = len(arr[0])
    for row in range(rows):
        for col in range(cols):
            output.append(arr[row][col])
    return output

def maxPrior(pixel):
    return max(pixel[0], pixel[1], pixel[2])

def allMaxPriors(flatImage, processes=1):
    p = Pool(processes)
    return p.map(maxPrior, flatImage)

def getMinPriorForGrid(image, xstart, xend, ystart, yend):
    output = 255
    for row in range(xstart, xend+1):
        for col in range(ystart, yend+1):
            for color in range(3):
                output = min(output, image[row][col][color])
    return output

def allMinPriors(image, rows, cols, omega=2):
    minPriors = []
    for row in range(rows):
        for col in range(cols):
            xstart = max(row-omega, 0)
            xend = min(row+omega, rows-1)
            ystart = max(col-omega, 0)
            yend = min(col+omega, cols-1)
            minPriors.append(getMinPriorForGrid(image, xstart, xend, ystart, yend))
    return minPriors

def showFlatImage(flatImage, rows, cols):
    index = 0
    image = []
    for row in range(rows):
        image.append([])
        for col in range(cols):
            image[row].append(flatImage[index])
            index += 1
    Image.showImage(image)

def airlight(flatImage):
    output = []
    for pixel in flatImage:
        output.append(float(pixel[0]+pixel[1]+pixel[2])/3)
    output = sorted(output, reverse=True)
    cutoff = len(flatImage)/1000
    return np.mean(output[:cutoff])

def defogPixel(inputArgs):
    pixel, minPriorVal, maxPriorVal, airLight = inputArgs
    outputPixel = []
    for color in range(3):
        value = max(float(airLight - pixel[color]), 0)
        maxPriorDepthMap = max(0, airLight-maxPriorVal) / airLight
        minPriorDepthMap = max(0, airLight-minPriorVal) / airLight
        depthMapVal = (maxPriorDepthMap + minPriorDepthMap) / 2
        value = min(value / max(depthMapVal, 0.5), 2500)
        value = max(airLight - value, 0)
        outputPixel.append(value)
    return outputPixel

def defogImage(flatImage, airLight, maxPriorVals, minPriorVals, processes=1):
    inputArgs = [(pixel, minPriorVals[index], maxPriorVals[index], airLight) for index, pixel in enumerate(flatImage)]
    p = Pool(processes)
    outputImage = p.map(defogPixel, inputArgs)
    return outputImage

def saveImage(flatImage, rows, cols):
    index = 0
    image = []
    for row in range(rows):
        image.append([])
        for col in range(cols):
            image[row].append(flatImage[index])
            index += 1
    Image.saveImage(image, './defogged_image.png')


def fastDefog(imageLocation, omega=2, processes=1):
    image = Image(imageLocation)
    image = image.getImageArray(convertToGrayScale=False)
    rows = len(image)
    cols = len(image[0])
    priors = None
    depthMapVal = None
    flatImage = flatten(image)
    flatSize = len(flatImage)
    maxPriors = allMaxPriors(flatImage, processes)
    minPriors = allMinPriors(image, rows, cols, omega)
    showFlatImage(maxPriors, rows, cols)
    showFlatImage(minPriors, rows, cols)
    airLight = airlight(flatImage)
    defoggedImage = defogImage(flatImage, airLight, maxPriors, minPriors, processes)
    for pixel in defoggedImage:
        pixel.append(255)
    showFlatImage(defoggedImage, rows, cols)

