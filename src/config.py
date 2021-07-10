import os
from pathlib import Path

class config:
    # Mode slection
    RAIN_ACCUMULATION_MODE  = True   # Lets the symbols fall in to position (Can take a while for large images)
    JUST_DISPLAY_MODE       = False   # Displays all the symbols at once
    
    
    # Window related
    SCREEN_HEIGHT   = 600
    SCREEN_WIDTH    = 1066
    FONT_SIZE       = 10
    FPS_LIMIT       = 500

    # Image related
    IMG_SCALE           = .7         # Image scaling (0.5 to half image size etc..)
    ISOLATE_COLOR       = (255,255,255)   # Color to isolate from image
    REPLACEMENT_COLORS  = []    # Colors for symbols for each occurance of isolate color (Default is white)
    THRESHOLD           = 60        # minimum % of (FONT_SIZE x FONT_SIZE) square that is ISOLATE_COLOR to be added to point

    # For screen fade effect
    STARTING_ALPHA  = 0     # In range 0-255 
    ALPHA_LIMIT     = 170   # 
    FADE_RATE       = 15    # How many frames till alpha value is increased by FADE_ADJUSTMENT
    FADE_ADJUSTMENT = 6

    # Paths
    ROOT_DIR        = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    
    IMG_FILENAME    = 'logo.png'
    IMG_PATH	    = os.path.join(ROOT_DIR, 'images/' + IMG_FILENAME)

    FONT_FILENAME   = 'MS Mincho.ttf'
    FONT_PATH       =  os.path.join(ROOT_DIR, 'font/' + FONT_FILENAME) 

    
    
