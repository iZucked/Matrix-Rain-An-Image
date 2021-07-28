import os
import sys
import time
from random import randrange

import pygame as pg

from config import Config
from image import image
from symbol import Symbol, SymbolColumn

os.environ["SDL_VIDEO_CENTERED"] = "1"


def main():
    TOGLE_DRAWING = True

    # MODE check
    if Config.JUST_DISPLAY_MODE and Config.RAIN_ACCUMULATION_MODE:
        print("CAN'T HAVE BOTH MODES ACTIVATED!, CHECK config.py")
        exit()

    if Config.DRAW_LINES_OF_IMAGE and Config.SINGLE_COLOR_SELECTION:
        print("Can't select more than one picture processing mode")
        exit()

    if len(sys.argv) != 2:
        print("Must add image to input in command line argument")
        exit()

    # Init pygame
    pg.init()

    # Set up image
    img = image(sys.argv[1])
    img.scale_image(Config.IMG_SCALE)
    startT = time.time()
    img.calculate_all_threshold_positions(
        Config.THRESHOLD, Config.FONT_SIZE, Config.ISOLATE_COLOR
    )
    if Config.debug:
        print(f"Time taken to calculate image points: {time.time() - startT}s")

    # Set up screen
    screen = pg.display.set_mode(
        (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pg.RESIZABLE
    )
    pg.display.set_caption("@CodeAccelerando on github")
    bg = pg.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
    alpha_value = Config.STARTING_ALPHA
    bg.set_alpha(alpha_value)
    clock = pg.time.Clock()

    # Set image to be centred in the screen
    screen_centre = (Config.SCREEN_WIDTH / 2, Config.SCREEN_HEIGHT / 2)
    img_center = img.get_centre()
    sX, sY = screen_centre
    iX, iY = img_center
    # Must be translated by terms of font size so they can be drawn to points
    # where the symbols should be
    vecX = round((sX - iX) / Config.FONT_SIZE)
    vecY = round((sY - iY) / Config.FONT_SIZE)

    startT = time.time()
    img.translate_points_by_vector(
        (vecX * Config.FONT_SIZE, vecY * Config.FONT_SIZE))
    if Config.debug:
        print(f"Time taken to translate image points: {time.time() - startT}s")

    # Set up symbol list for JUST_DISPLAY_MODE if toggled
    symbol_list = []
    if Config.JUST_DISPLAY_MODE:
        for x, yPositions in img.columnPositions.items():
            for y in yPositions:
                symbol_list.append(Symbol(x, y, 0, pg.Color("white")))

    # Create a column for each (x, x + FONT_SIZE) in the screen
    symbol_columns = [
        SymbolColumn(
            x, randrange(0, Config.SCREEN_HEIGHT), img.get_positions_for_column(x)
        )
        for x in range(0, Config.SCREEN_WIDTH, Config.FONT_SIZE)
    ]

    while True:
        # Check for events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

        # Create black background for screen
        screen.blit(bg, (0, 0))
        bg.fill(pg.Color("black"))

        if Config.RAIN_ACCUMULATION_MODE and TOGLE_DRAWING:
            if img.columns_left_to_place():
                for symbol_column in symbol_columns:
                    if img.column_has_positions(symbol_column.x) and (
                        symbol_column.get_white_symbol().get_y_position()
                        == img.get_next_position_for_column(symbol_column.x)
                    ):
                        symbol_column.place_white_symbol()
                        img.get_positions_for_column(symbol_column.x).pop(0)

        elif Config.JUST_DISPLAY_MODE and TOGLE_DRAWING:
            for symbol in symbol_list:
                symbol.update()
                symbol.draw(bg)

        # Draw all columns
        for symbol_column in symbol_columns:
            symbol_column.draw(bg)

        # Alpha max is 255 where there is no fading
        if (
                not pg.time.get_ticks() % Config.FADE_RATE
                and alpha_value < Config.ALPHA_LIMIT
        ):
            alpha_value += Config.FADE_ADJUSTMENT
            bg.set_alpha(alpha_value)

        # Check if user wants to start placing image
        keys_pressed = pg.key.get_pressed()
        if keys_pressed[pg.K_RETURN]:
            TOGLE_DRAWING = not TOGLE_DRAWING

        pg.display.update()
        clock.tick(Config.FPS_LIMIT)


if __name__ == "__main__":
    main()
