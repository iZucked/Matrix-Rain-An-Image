from PIL import Image
import os
import math
import pygame
from config import config
from pathlib import Path


debug = False

# define FPS
FPS = 120
    
# Define clock for fps
clock = pygame.time.Clock()

# Set window title
pygame.display.set_caption("Our sick window blud!!")

class image:
    def __init__(self, filePath):
        self.imgObj = Image.open(Path(filePath))
        self.imgScale = 1
        self.columnPositions = {}
        self.readyToDraw = False

    def getDimensions(self):
        return self.imgObj.size

    def getCentre(self):
        x,y = self.getDimensions()
        return (x/2,y/2)

    def scaleImage(self, scaleFactor):
        x, y = self.getDimensions()
        newDimensions = (x*scaleFactor , y*scaleFactor)
        self.imgObj.thumbnail(newDimensions, Image.ANTIALIAS)

    def isRegionThisColor(self, xStart, yStart, size, threshold, color):
        # Get image data
        rgb_img = self.imgObj.convert('RGB')
        
        # Number of occourances of colour specified
        nOccurances = 0 
        
        r0,g0,b0 = color

        for y in range(yStart, yStart + size):
            for x in range(xStart, xStart + size):
                r, g, b = rgb_img.getpixel((x,y))
                
                if debug:
                    print(f'Pixel at : {x},{y} has color ({r},{g},{b})')
                
                if (r,g,b) == (r0,g0,b0):
                    nOccurances+=1
            
        pOccurances = (nOccurances/math.pow(size,2))*100

        if pOccurances >= threshold:
            
            return True
        else:
            return False
    
        if debug:
            print(f'Numer of occourances:{nOccurances}')
            print(f'Percentage: {(nOccurances/math.pow(size,2))*100}%')        

    def calculateAllThresholdPositions(self, threshold, size, color):
        width, length = self.getDimensions()

        if debug:
            print(f'Image Size: {width} x {length}')

        for x in range(0, width - size, size):
            yPositions = []
            for y in range(0, length - size, size):
                if debug:
                    print(f'{x},{y} -> {x+size}, {y+size}')
                if self.isRegionThisColor(x,y,size,threshold,color):
                    yPositions.append(y)
                    if debug:
                        print("Met threshold!")
                else:
                    if debug:
                        print("Didn't Meet threshold!")
            yPositions.sort(reverse=True)
            self.columnPositions.update({x : yPositions})
        
        self.readyToDraw = True

    def translatePointsByVector(self, vector):
        if self.columnPositions != {}:
            vecX, vecY = vector
            newPoints = {}
            newPoints = {xPos + vecX : [yPos + vecY for yPos in yPositons] for (xPos, yPositons) in self.columnPositions.items() }
            self.columnPositions = newPoints
        else:
            print("Must calculate points to translate first")



    def getPositionsForColumn(self, columnPos):
        if self.columnHasPositions(columnPos):
            return self.columnPositions[columnPos]
        else:
            return []

    def columnsLeftToPlace(self):
        for column in self.getColumns():
            if self.columnHasPositions(column):
                return True
        return False

    def columnHasPositions(self, columnPos):
        if columnPos in self.columnPositions:
            return len(self.columnPositions[columnPos]) > 0
        else:
            return False

    def getNextPositionForColumn(self, columnNum):
        return self.columnPositions[columnNum][0]

    def getColumns(self):
        return self.columnPositions.keys()

    def getNumColumns(self):
        return len(self.columnPositions.keys())

    def isReadyToDraw(self):
        return self.readyToDraw


def main():
    # Open image and scale it
    img = image(config.IMG_PATH)
    img.scaleImage(1)
    
    width, length = img.getDimensions()
    WIN = pygame.display.set_mode((width,length))

    size = config.FONT_SIZE

    img.calculateAllThresholdPositions(30, config.FONT_SIZE, (0,0,0))

    print("Finished calculating")

    if img.columnsLeftToPlace():
        print("Does have columns left")

    while True:
        # Let clock tick
        clock.tick(FPS)

        if img.columnsLeftToPlace():
            for x in range(0, config.SCREEN_WIDTH, config.FONT_SIZE):
                if img.columnHasPositions(x):
                    y = img.getPositionsForColumn(x).pop(0)
                    clock.tick(FPS)
                    WIN.fill((0,0,0),(pygame.Rect(x,y,size,size)))
                    WIN.fill((255,255,255),(pygame.Rect(x,y,size-1,size-1)))
                    pygame.display.update()

        # Getting events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        # Update frame
        pygame.display.update()

if __name__ == "__main__":
    main()


