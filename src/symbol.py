import pygame as pg
from random import choice, randrange
from config import config
import time

NOT_PLACED  = 0x00
PLACED      = 0x01

class Symbol:
    def __init__(self, x, y, speed, characterSet):
        self.x, self.y = x, y
        self.speed = speed
        self.surface = choice(characterSet)
        self.interval = randrange(5, 30)
        self.charSet = characterSet
        self.state = NOT_PLACED

    def update(self):
        frames = pg.time.get_ticks()

        if not frames % self.interval:
            self.surface = choice(self.charSet)

        if self.state == NOT_PLACED:
            self.y = self.y + self.speed if self.y < config.SCREEN_HEIGHT else -config.FONT_SIZE

        return self

    def getYPosition(self):
        return self.y

    def stop_moving(self):
        self.state = PLACED

class SymbolColumn:
    def __init__(self, xPos, startY, placeablePositionsList):
        # Create our list of characters we can render which then is made in to a list of surfaces
        katakana = [chr(int('0x30a0', 16) + i) for i in range(96)]
        font = pg.font.Font('font/MS Mincho.ttf', config.FONT_SIZE, bold=True)
        green_katakana = [font.render(char, True, (40, randrange(160, 256), 40)) for char in katakana]
        lightgreen_katakana = [font.render(char, True, pg.Color('lightgreen')) for char in katakana]
        white_katakana = [font.render(char, True, pg.Color('white')) for char in katakana]
        
        minLength = 8
        maxLength = 50
        minSpeed = 10
        maxSpeed = 20
        
        self.startY = startY
        self.x = xPos
        self.column_height = randrange(minLength, maxLength)
        self.speed = randrange(minSpeed, maxSpeed, 10)
        self.symbols = []
        self.placedSymbols = []
        self.placeablePositions = placeablePositionsList

        n = 0
        for i in range(startY, startY - config.FONT_SIZE * self.column_height, -config.FONT_SIZE):
            if n == 0:
                # Let first symbol be white
                self.symbols.append(Symbol(xPos, i, self.speed, white_katakana))
            elif  n % 2 :
                self.symbols.append(Symbol(xPos, i, self.speed, green_katakana))
            else:
                self.symbols.append(Symbol(xPos, i, self.speed, lightgreen_katakana)) 
            
            n=+1

    def placeWhiteSymbol(self):
        # Add placed symbol and replace with new one
        copy_list = self.symbols.copy()
        whiteSymbol = copy_list[0]
        whiteSymbol.stop_moving()
        self.placedSymbols.append(whiteSymbol)
        self.symbols[0] = Symbol(whiteSymbol.x, whiteSymbol.y, whiteSymbol.speed, whiteSymbol.charSet)

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
            surface.blit(symbol.surface, (symbol.x, symbol.y))

        # Draw all placed symbols
        for symbol in self.placedSymbols:
            symbol.update()
            surface.blit(symbol.surface, (symbol.x, symbol.y))
