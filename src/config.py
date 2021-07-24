import os
from pathlib import Path


class config:
    # Mode slection
    RAIN_ACCUMULATION_MODE = False  # Lets the symbols fall in to position (Can take a while for large images)
    JUST_DISPLAY_MODE = True  # Displays all the symbols at once

    # Window related
    SCREEN_WIDTH = 1260
    SCREEN_HEIGHT = 800
    FONT_SIZE = 7
    FPS_LIMIT = 60

    # Image Modes
    SINGLE_COLOR_SELECTION = False  # Selects an ISOLATE_COLOR and draws a symbol where found in a FONT_SIZE x FONT_SIZE square
    DRAW_LINES_OF_IMAGE = True

    # Image related
    IMG_SCALE = 0.8  # Image scaling (0.5 to half image size etc..)
    ISOLATE_COLOR = (255, 255, 255)  # Color to isolate from image
    REPLACEMENT_COLORS = (
        []
    )  # Colors for symbols for each occurance of isolate color (Default is white)
    THRESHOLD = 30  # minimum % of (FONT_SIZE x FONT_SIZE) square that is ISOLATE_COLOR to be added to point

    # For screen fade effect
    STARTING_ALPHA = 60  # In range 0-255
    ALPHA_LIMIT = 170  #
    FADE_RATE = 15  # How many frames till alpha value is increased by FADE_ADJUSTMENT
    FADE_ADJUSTMENT = 6

    # Paths
    ROOT_DIR = os.getcwd()

    IMG_FILENAME = "garf.png"
    IMG_PATH = os.path.join(ROOT_DIR, "images/" + IMG_FILENAME)

    FONT_FILENAME = "MS Mincho.ttf"
    FONT_PATH = os.path.join(ROOT_DIR, "font/" + FONT_FILENAME)
