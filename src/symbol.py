import pygame as pg
from random import choice, randrange
from config import config
import time

NOT_PLACED  = 0x00
PLACED      = 0x01



class Symbol:
    def __init__(self, x, y, speed, color):
        # Create our list of characters we can render which then is made in to a list of surfaces
        katakana = [chr(int('0x30a0', 16) + i) for i in range(96)]
        font = pg.font.Font(config.FONT_PATH, config.FONT_SIZE, bold=True)

        self.x, self.y = x, y
        self.speed = speed
        self.color = color
        self.interval = randrange(5, 30)
        self.state = NOT_PLACED
        self.charSet = [font.render(char, True, color) for char in katakana]
        self.surface = choice(self.charSet)

    def update(self):
        frames = pg.time.get_ticks()

        if not frames % self.interval:
            self.surface = choice(self.charSet)

        if self.state == NOT_PLACED:
            self.y = self.y + self.speed if self.y < config.SCREEN_HEIGHT else -config.FONT_SIZE

        return self

    def draw(self, surface):
        surface.blit(self.surface, (self.x, self.y))

    def getYPosition(self):
        return self.y

    def stop_moving(self):
        self.state = PLACED

class SymbolColumn:
    def __init__(self, xPos, startY, placeablePositionsList):        
        minLength = 8
        maxLength = 50
        minSpeed = 1 * config.FONT_SIZE
        maxSpeed = 2 * config.FONT_SIZE
        
        self.startY = startY
        self.x = xPos
        self.column_height = randrange(minLength, maxLength)
        self.speed = config.FONT_SIZE#randrange(minSpeed, maxSpeed, config.FONT_SIZE)
        self.symbols = []
        self.placedSymbols = []
        self.placeablePositions = placeablePositionsList

        n = 0
        for i in range(startY, startY - config.FONT_SIZE * self.column_height, -config.FONT_SIZE):
            if n == 0:
                # Let first symbol be white
                self.symbols.append(Symbol(xPos, i, self.speed, pg.Color('white')))
            elif  n % 2 :
                self.symbols.append(Symbol(xPos, i, self.speed, (40, randrange(160, 256), 40)))
            else:
                self.symbols.append(Symbol(xPos, i, self.speed, pg.Color('lightgreen'))) 
            
            n=+1

    def placeWhiteSymbol(self):
        # Add placed symbol and replace with new one
        copy_list = self.symbols.copy()
        whiteSymbol = copy_list[0]
        whiteSymbol.stop_moving()
        self.placedSymbols.append(whiteSymbol)
        self.symbols[0] = Symbol(whiteSymbol.x, whiteSymbol.y, whiteSymbol.speed, whiteSymbol.color)

    def getWhiteSymbol(self):
        return self.symbols[0]

    def checkWhiteSymbol(self):
        if self.getWhiteSymbol().getYPosition() == self.nextPlacementPos and self.nextPlacementPos != -1:
            #print(f"placing white at: {self.nextPlacementPos}")
            if len(self.placeablePositions) > 0:
                self.nextPlacementPos = self.placeablePositions.pop(0)
            else:
                self.nextPlacementPos = -1 # Unreachable

            self.placeWhiteSymbol()

    def draw(self, surface):
        # Check if we need to place any symbols
        #self.checkWhiteSymbol()

        # Draw all moving symbols
        for i, symbol in enumerate(self.symbols):
            if symbol.state == PLACED:
                print(f"SYMBOL {symbol.x} should not be here!!!!!!!!!!!!")
            
            # Update the symbol character and position
            symbol.update()

            # Add fading effect in the column
            symbol.surface.set_alpha(i + (255 - (255 / self.column_height)*i))

            # Draw symbol to surface
            symbol.draw(surface)

        # Draw all placed symbols
        for symbol in self.placedSymbols:
            symbol.update()
            surface.blit(symbol.surface, (symbol.x, symbol.y))
