import os
import pygame as pg
from random import choice, randrange
from image import image
from config import config
from symbol import Symbol, SymbolColumn
import multiprocessing
import time


os.environ['SDL_VIDEO_CENTERED'] = '1'
RES = config.SCREEN_WIDTH, config.SCREEN_HEIGHT




def main():
    # Init pygame
    pg.init()

    # Set up screen
    screen = pg.display.set_mode(RES, pg.RESIZABLE)
    bg = pg.Surface(RES)
    alpha_value = config.STARTING_ALPHA
    bg.set_alpha(alpha_value)
    clock = pg.time.Clock()
    
    # Set up image
    img = image(config.IMG_FILENAME)
    img.scaleImage(0.7)
    white = (255,255,255)
    img.calculateAllThresholdPositions(90,config.FONT_SIZE,white)

    # Create a column for each (x, x + FONT_SIZE) in the screen
    symbol_columns = [SymbolColumn(x, randrange(0, config.SCREEN_HEIGHT), img.getPositionsForColumn(x)) for x in range(0, config.SCREEN_WIDTH, config.FONT_SIZE)]

    while True:
        # Check for events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.VIDEORESIZE:
                bg = pg.transform.scale(bg, event.dict['size'],screen)
            elif event.type == pg.VIDEOEXPOSE:  # handles window minimising/maximising
                bg = pg.transform.scale(bg, screen.get_size(),screen)
        
        # Create black background for screen
        screen.blit(bg, (0, 0))
        bg.fill(pg.Color('black'))

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
        if keys_pressed[pg.K_a]: # Left
            pg.display.toggle_fullscreen()



        
        
                        
        
        pg.display.flip()
        clock.tick(config.FPS_LIMIT)

if __name__ == "__main__":
    main()