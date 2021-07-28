import os
import sys
import time
from random import randrange

import pygame

from config import Config
from image import Image
from symbol import Symbol, SymbolColumn

os.environ["SDL_VIDEO_CENTERED"] = "1"


def mode_check():
    # MODE check
    if Config.JUST_DISPLAY_MODE and Config.RAIN_ACCUMULATION_MODE:
        print("CAN'T HAVE BOTH MODES ACTIVATED!, CHECK config.py")
        return False

    if Config.DRAW_LINES_OF_IMAGE and Config.SINGLE_COLOR_SELECTION:
        print("Can't select more than one picture processing mode")
        return False

    if len(sys.argv) != 2:
        print("Must add image to input in command line argument")
        return False

    return True


def main():
    toggle_drawing = True

    if not mode_check():
        return

    pygame.init()

    # Set up image
    img = Image(sys.argv[1])
    img.scale_image(Config.IMG_SCALE)
    start_time = time.time()

    img.calculate_all_threshold_positions(
        Config.FONT_SIZE, Config.ISOLATE_COLOR
    )

    if Config.debug:
        print(
            f"Time taken to calculate image points: {time.time() - start_time}s"
        )

    # Set up screen
    screen = pygame.display.set_mode(
        (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.RESIZABLE
    )
    pygame.display.set_caption("@CodeAccelerando on github")
    background = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
    alpha_value = Config.STARTING_ALPHA
    background.set_alpha(alpha_value)
    clock = pygame.time.Clock()

    # Set image to be centred in the screen
    screen_centre = (Config.SCREEN_WIDTH / 2, Config.SCREEN_HEIGHT / 2)

    img_center = img.get_centre()
    s_x, s_y = screen_centre
    i_x, i_y = img_center

    # Must be translated by terms of font size so they can be drawn to points
    # where the symbols should be
    vec_x = round((s_x - i_x) / Config.FONT_SIZE)
    vec_y = round((s_y - i_y) / Config.FONT_SIZE)

    start_time = time.time()
    img.translate_points_by_vector(
        (vec_x * Config.FONT_SIZE, vec_y * Config.FONT_SIZE)
    )

    if Config.debug:
        print(
            f"Time taken to translate image points: {time.time() - start_time}s"
        )

    # Set up symbol list for JUST_DISPLAY_MODE if toggled
    symbol_list = []
    if Config.JUST_DISPLAY_MODE:
        for x, yPositions in img.column_positions.items():
            for y in yPositions:
                symbol_list.append(Symbol(x, y, 0, pygame.Color("white")))

    # Create a column for each (x, x + FONT_SIZE) in the screen
    symbol_columns = [
        SymbolColumn(
            x, randrange(0, Config.SCREEN_HEIGHT),
            img.get_positions_for_column(x)
        )
        for x in range(0, Config.SCREEN_WIDTH, Config.FONT_SIZE)
    ]

    is_running = True
    while is_running:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        # Create black background for screen
        screen.blit(background, (0, 0))
        background.fill(pygame.Color("black"))

        if (
            Config.RAIN_ACCUMULATION_MODE
                and toggle_drawing
                and img.columns_left_to_place()
        ):
            for symbol_column in symbol_columns:
                if (
                    img.column_has_positions(symbol_column.x) and (
                        symbol_column.get_white_symbol().get_y_position()
                        == img.get_next_position_for_column(symbol_column.x)
                    )
                ):
                    symbol_column.place_white_symbol()
                    img.get_positions_for_column(symbol_column.x).pop(0)

        elif Config.JUST_DISPLAY_MODE and toggle_drawing:
            for symbol in symbol_list:
                symbol.update()
                symbol.draw(background)

        # Draw all columns
        for symbol_column in symbol_columns:
            symbol_column.draw(background)

        # Alpha max is 255 where there is no fading
        if (
            not pygame.time.get_ticks() % Config.FADE_RATE
                and alpha_value < Config.ALPHA_LIMIT
        ):
            alpha_value += Config.FADE_ADJUSTMENT
            background.set_alpha(alpha_value)

        # Check if user wants to start placing image
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_RETURN]:
            toggle_drawing = not toggle_drawing

        pygame.display.update()
        clock.tick(Config.FPS_LIMIT)

    pygame.display.quit()
    pygame.quit()


if __name__ == "__main__":
    main()
