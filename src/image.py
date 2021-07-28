import numpy as np
from PIL import Image
import cv2
import numpy as np
import os
import sys
import math
import pygame
from config import config
from pathlib import Path
import time


class image:
    def __init__(self, filePath):
        image = cv2.imread(filePath)

        if image is None:
            print(f"ERROR: Can't open image at: {filePath}")
            exit()

        if config.SINGLE_COLOR_SELECTION:
            self.imgObj = image
        # Do pre-processing if DRAW_LINES_OF_IMAGE is enabled
        elif config.DRAW_LINES_OF_IMAGE:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            lines = cv2.Canny(image, 10, 200)
            whitePx = np.where(lines == 255)
            cnts = cv2.findContours(lines, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            for c in cnts:
                cv2.drawContours(lines, [c], -1, config.ISOLATE_COLOR,
                                 thickness=config.LINE_THICKNESS)

            # Convert back from graysacle([0-255]) to rgb([0-255,0-255,0-255])
            self.imgObj = cv2.cvtColor(lines, cv2.COLOR_GRAY2RGB)

            if config.debug:
                cv2.imshow("Image converted", self.imgObj)
                cv2.waitKey(0)

        self.path = filePath
        self.columnPositions = {}

    def getDimensions(self):
        y, x, _ = self.imgObj.shape
        return x, y

    def getCentre(self):
        x, y = self.getDimensions()
        return x / 2, y / 2

    def scaleImage(self, scaleFactor):
        x, y = self.getDimensions()
        newDimensions = (int(x * scaleFactor), int(y * scaleFactor))
        self.imgObj = cv2.resize(self.imgObj, newDimensions,
                                 interpolation=cv2.INTER_AREA)

        if config.debug:
            print(f"New dimensions: {newDimensions}")

    def calculateAllThresholdPositions(self, threshold, size, color):
        width, length = self.getDimensions()

        # Apply mask to image
        if config.SINGLE_COLOR_SELECTION:
            mask = cv2.inRange(self.imgObj, color, color)
        elif config.DRAW_LINES_OF_IMAGE:
            mask = cv2.inRange(self.imgObj, (255, 255, 255), (255, 255, 255))

        if config.debug:
            cv2.imshow("Masked image", mask)
            cv2.waitKey(0)

        # Code provided by https://github.com/ilastik/lazyflow/blob/master/lazyflow/utility/blockwise_view.py, an absolute god send
        # This compared to the other version is ~5000x faster
        # Breaks image down to submatracies of sizexsize and then checks if the mask has values
        blockshape = tuple((size, size))
        outershape = tuple(np.array(mask.shape) // blockshape)
        view_shape = outershape + blockshape

        if config.debug:
            print(f"block shape: {blockshape}")
            print(f"outer shape: {outershape}")
            print(f"View shape: {view_shape}")

        # inner strides: strides within each block (same as original array)
        intra_block_strides = mask.strides

        # outer strides: strides from one block to another
        inter_block_strides = tuple(mask.strides * np.array(blockshape))

        # This is where the magic happens.
        # Generate a view with our new strides (outer+inner).
        subMatracies = np.lib.stride_tricks.as_strided(mask, shape=view_shape,
                                                       strides=(
                                                                   inter_block_strides + intra_block_strides))

        subLen, subWid, _, _ = subMatracies.shape

        # Loop through all submatracies and
        for x in range(0, subWid - 1):
            yPositions = []
            for y in range(0, subLen - 1):
                # Check if passes threshold occurances of color in submatrix
                nOccerances = np.count_nonzero(subMatracies[y][x])
                pOccuracnes = (nOccerances / math.pow(size, 2)) * 100
                if pOccuracnes >= config.THRESHOLD:
                    yPositions.append(y * size)
            if len(yPositions) > 0:
                yPositions.sort(reverse=True)
                self.columnPositions.update({x * size: yPositions})

    def translatePointsByVector(self, vector):
        if self.columnPositions != {}:
            vecX, vecY = vector
            newPoints = {}
            newPoints = {xPos + vecX: [yPos + vecY for yPos in yPositons] for
                         (xPos, yPositons) in self.columnPositions.items()}
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


def main():
    # Define clock for fps
    clock = pygame.time.Clock()

    # Set window title
    pygame.display.set_caption("Image to font boxes calculated")

    # Open image and scale it
    img = image(sys.argv[1])
    img.scaleImage(config.IMG_SCALE)

    width, length = img.getDimensions()
    WIN = pygame.display.set_mode((width, length))

    start = time.time()
    img.calculateAllThresholdPositions(config.THRESHOLD, config.FONT_SIZE,
                                       config.ISOLATE_COLOR)
    finish = time.time()

    print(f"Finished calculating points in {finish - start} seconds")

    if not img.columnsLeftToPlace():
        print("Couldn't calculate any positions to draw")
        quit()

    stopDrawing = False

    while True:
        # Let clock tick
        clock.tick(config.FADE_RATE)

        if not stopDrawing:
            for x, yPositions in img.columnPositions.items():
                for y in yPositions:
                    WIN.fill((0, 0, 0), (
                        pygame.Rect(x, y, config.FONT_SIZE, config.FONT_SIZE)))
                    WIN.fill((255, 255, 255), (
                        pygame.Rect(x, y, config.FONT_SIZE - 1,
                                    config.FONT_SIZE - 1)))
                    stopDrawing = True

        # Getting events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        # Update frame
        pygame.display.update()


if __name__ == "__main__":
    main()
