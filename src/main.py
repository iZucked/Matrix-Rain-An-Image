import os
import sys
import cv2
import pygame as pg
from random import choice, randrange
from image import image
from config import config
from symbol import Symbol, SymbolColumn
import time

os.environ["SDL_VIDEO_CENTERED"] = "1"


def main():
    TOGLE_DRAWING = True

    # MODE check
    if config.JUST_DISPLAY_MODE and config.RAIN_ACCUMULATION_MODE:
        print("CAN'T HAVE BOTH MODES ACTIVATED!, CHECK config.py")
        exit()

    if config.DRAW_LINES_OF_IMAGE and config.SINGLE_COLOR_SELECTION:
        print("Can't select more than one picture processing mode")
        exit()

    if len(sys.argv) != 2:
        print("Must add image to input in command line argument")
        exit()

    # Init pygame
    pg.init()

    # Set up image
    img = image(sys.argv[1])
    img.scaleImage(config.IMG_SCALE)
    startT = time.time()
    img.calculateAllThresholdPositions(
        config.THRESHOLD, config.FONT_SIZE, config.ISOLATE_COLOR
    )
    print(f"Time taken to calculate image points: {time.time() - startT}s")

    # Set up screen
    screen = pg.display.set_mode(
        (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pg.RESIZABLE
    )
    pg.display.set_caption("@CodeAccelerando on github")
    bg = pg.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    alpha_value = config.STARTING_ALPHA
    bg.set_alpha(alpha_value)
    clock = pg.time.Clock()

    # Set image to be centred in the screen
    screen_centre = (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2)
    img_center = img.getCentre()
    sX, sY = screen_centre
    iX, iY = img_center
    # Must be translated by terms of font size so they can be drawn to points where the symbols should be
    vecX = round((sX - iX) / config.FONT_SIZE)
    vecY = round((sY - iY) / config.FONT_SIZE)
    img.translatePointsByVector((vecX * config.FONT_SIZE, vecY * config.FONT_SIZE))

    # Set up symbol list for JUST_DISPLAY_MODE if toggled
    symbol_list = []
    if config.JUST_DISPLAY_MODE:
        for x, yPositions in img.columnPositions.items():
            for y in yPositions:
                symbol_list.append(Symbol(x, y, 0, pg.Color("white")))

    # Create a column for each (x, x + FONT_SIZE) in the screen
    symbol_columns = [
        SymbolColumn(
            x, randrange(0, config.SCREEN_HEIGHT), img.getPositionsForColumn(x)
        )
        for x in range(0, config.SCREEN_WIDTH, config.FONT_SIZE)
    ]

    while True:
        # Check for events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

        # Create black background for screen
        screen.blit(bg, (0, 0))
        bg.fill(pg.Color("black"))

        if config.RAIN_ACCUMULATION_MODE and TOGLE_DRAWING:
            if img.columnsLeftToPlace():
                for symbol_column in symbol_columns:
                    if img.columnHasPositions(symbol_column.x):
                        if (
                            symbol_column.getWhiteSymbol().getYPosition()
                            == img.getNextPositionForColumn(symbol_column.x)
                        ):
                            symbol_column.placeWhiteSymbol()
                            img.getPositionsForColumn(symbol_column.x).pop(0)
        elif config.JUST_DISPLAY_MODE and TOGLE_DRAWING:
            for symbol in symbol_list:
                symbol.update()
                symbol.draw(bg)

        # Draw all columns
        for symbol_column in symbol_columns:
            symbol_column.draw(bg)

        # Alpha max is 255 where there is no fading
        if (
            not pg.time.get_ticks() % config.FADE_RATE
            and alpha_value < config.ALPHA_LIMIT
        ):
            alpha_value += config.FADE_ADJUSTMENT
            bg.set_alpha(alpha_value)

        # Check if user wants to start placing image
        keys_pressed = pg.key.get_pressed()
        if keys_pressed[pg.K_RETURN]:
            TOGLE_DRAWING = not TOGLE_DRAWING

        pg.display.update()
        clock.tick(config.FPS_LIMIT)


if __name__ == "__main__":
    main()
