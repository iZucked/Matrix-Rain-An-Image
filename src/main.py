import os
import pygame as pg
from random import choice, randrange
from image import image
from config import config
from symbol import Symbol, SymbolColumn
import time

os.environ['SDL_VIDEO_CENTERED'] = '1'
RES = config.SCREEN_WIDTH, config.SCREEN_HEIGHT

def main():
    TOGLE_DRAWING = True
    
    # Init pygame
    pg.init()

    # Set up image
    img = image(config.IMG_PATH)
    img.scaleImage(config.IMG_SCALE)
    img.calculateAllThresholdPositions(config.THRESHOLD, config.FONT_SIZE, config.ISOLATE_COLOR)

    # Set up screen
    screen = pg.display.set_mode(RES, pg.RESIZABLE)
    pg.display.set_caption("@CodeAccelerando on github")
    bg = screen#pg.Surface(RES)
    alpha_value = config.STARTING_ALPHA
    bg.set_alpha(alpha_value)
    clock = pg.time.Clock()
    
    # Set image to be centred in the screen
    screen_centre = (config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT/2)
    img_center = img.getCentre()
    sX, sY = screen_centre
    iX, iY = img_center
    # Must be translated by terms of font size so they can be drawn to points where the symbols should be
    vecX = round((sX - iX)/config.FONT_SIZE)
    vecY = round((sY - iY)/config.FONT_SIZE)
    img.translatePointsByVector((vecX*config.FONT_SIZE, vecY*config.FONT_SIZE))

    # Create a column for each (x, x + FONT_SIZE) in the screen
    symbol_columns = [SymbolColumn(x, randrange(0, config.SCREEN_HEIGHT), img.getPositionsForColumn(x)) for x in range(0, config.SCREEN_WIDTH, config.FONT_SIZE)]

    for column in symbol_columns:
        for pos in column.placeablePositions:
            if pos % config.FONT_SIZE != 0:
                print(f"{pos} isn't divisible")

    while True:
        # Check for events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
        
        # Create black background for screen
        screen.blit(bg, (0, 0))
        bg.fill(pg.Color('black'))

        # Check if symbol is in it's next column symbol position to be placed and if so pause it's motion
        if TOGLE_DRAWING:
            if img.columnsLeftToPlace():
                for symbol_column in symbol_columns:
                    if img.columnHasPositions(symbol_column.x):
                        if symbol_column.getWhiteSymbol().getYPosition() == img.getNextPositionForColumn(symbol_column.x):
                            symbol_column.placeWhiteSymbol()
                            img.getPositionsForColumn(symbol_column.x).pop(0)
        
        # Draw all columns
        for symbol_column in symbol_columns:
            symbol_column.draw(bg)
            
        # Alpha max is 255 where there is no fading
        if not pg.time.get_ticks() % config.FADE_RATE and alpha_value < config.ALPHA_LIMIT:
            alpha_value += config.FADE_ADJUSTMENT
            bg.set_alpha(alpha_value)

        # Check if user wants to start placing image
        keys_pressed = pg.key.get_pressed()
        if keys_pressed[pg.K_RETURN]: # Left
            TOGLE_DRAWING = not TOGLE_DRAWING

        pg.display.flip()
        clock.tick(config.FPS_LIMIT)

if __name__ == "__main__":
    main()