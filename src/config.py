import os


class Config:
    # Enable or disable debug messages
    debug = False

    # Draw Modes
    RAIN_ACCUMULATION_MODE = False
    # Lets the symbols fall in to position (Can take a while for large images)
    JUST_DISPLAY_MODE = True  # Displays all the symbols at once

    # Image Processing Modes

    SINGLE_COLOR_SELECTION = True
    # Selects an ISOLATE_COLOR and draws a symbol where found in a
    # FONT_SIZE x FONT_SIZE square
    DRAW_LINES_OF_IMAGE = False
    LINE_THICKNESS = 2  # If DRAW_LINES_OF_IMAGE is chosen the lines of an image
    # must be big enough to fit a FONT_SIZE x FONT_SIZE square of white pixels
    # (change and enable debug to see difference)

    # Window related
    SCREEN_WIDTH = 1260
    SCREEN_HEIGHT = 800

    SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

    FONT_SIZE = 10
    FPS_LIMIT = 60

    # Image related
    IMG_SCALE = 0.8  # Image scaling (0.5 to half image size etc..)
    ISOLATE_COLOR = (255, 255, 255)  # Color to isolate from image
    THRESHOLD = 30  # minimum % of (FONT_SIZE x FONT_SIZE) square that is
    # ISOLATE_COLOR to be added to point

    # For screen fade effect
    STARTING_ALPHA = 60  # In range 0-255
    ALPHA_LIMIT = 170
    FADE_RATE = 15
    # How many frames till alpha value is increased by FADE_ADJUSTMENT
    FADE_ADJUSTMENT = 6

    # Paths
    ROOT_DIR = os.getcwd()

    if ROOT_DIR.endswith('src'):
        ROOT_DIR = ROOT_DIR[:-3]

    IMG_FILENAME = "logo.png"
    IMG_PATH = os.path.join(ROOT_DIR, "images/" + IMG_FILENAME)
    
    FONT_FILENAME = "MS Mincho.ttf"
    FONT_PATH = os.path.join(ROOT_DIR, "font/" + FONT_FILENAME)
