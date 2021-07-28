from random import choice, randrange

import pygame as pg

from config import Config

NOT_PLACED = 0x00
PLACED = 0x01

pg.init()

# Create our list of characters we can render which then is made in to a
# list of surfaces
katakana = [chr(int('0x30a0', 16) + i) for i in range(96)]
font = pg.font.Font(Config.FONT_PATH, Config.FONT_SIZE)


class Symbol:
    def __init__(self, x, y, speed, color):
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
            self.y = self.y + self.speed \
                if self.y < Config.SCREEN_HEIGHT else -Config.FONT_SIZE

        return self

    def draw(self, surface):
        surface.blit(self.surface, (self.x, self.y))

    def get_y_position(self):
        return self.y

    def stop_moving(self):
        self.state = PLACED


class SymbolColumn:
    def __init__(self, pos_x, start_y, placeable_positions_list):
        min_length = 8
        max_length = 35
        self.startY = start_y
        self.x = pos_x
        self.column_height = randrange(min_length, max_length)
        if Config.RAIN_ACCUMULATION_MODE:
            self.speed = Config.FONT_SIZE
        else:
            min_speed = 3
            max_speed = 8

            self.speed = randrange(min_speed, max_speed)
        self.symbols = []
        self.placedSymbols = []
        self.placeablePositions = placeable_positions_list

        n = 0
        for i in range(start_y, start_y - Config.FONT_SIZE * self.column_height,
                       -Config.FONT_SIZE):
            if n == 0:
                # Let first symbol be white
                self.symbols.append(
                    Symbol(pos_x, i, self.speed, pg.Color('white')))
            elif n % 2:
                self.symbols.append(
                    Symbol(pos_x, i, self.speed, (40, randrange(160, 256), 40)))
            else:
                self.symbols.append(
                    Symbol(pos_x, i, self.speed, pg.Color('lightgreen')))

            n = +1

    def place_white_symbol(self):
        # Add placed symbol and replace with new one
        copy_list = self.symbols.copy()
        white_symbol = copy_list[0]
        white_symbol.stop_moving()
        self.placedSymbols.append(white_symbol)
        self.symbols[0] = Symbol(
            white_symbol.x,
            white_symbol.y,
            white_symbol.speed,
            white_symbol.color
        )

    def get_white_symbol(self):
        return self.symbols[0]

    def check_white_symbol(self):
        if (
            self.get_white_symbol().get_y_position() == self.next_placement_pos
            and self.next_placement_pos != -1
        ):
            # print(f"placing white at: {self.nextPlacementPos}")
            if len(self.placeablePositions) > 0:
                self.next_placement_pos = self.placeablePositions.pop(0)
            else:
                self.next_placement_pos = -1  # Unreachable

            self.place_white_symbol()

    def draw(self, surface):
        # Check if we need to place any symbols
        # self.checkWhiteSymbol()

        # Draw all moving symbols
        for i, symbol in enumerate(self.symbols):
            if symbol.state == PLACED:
                print(f"SYMBOL {symbol.x} should not be here!!!!!!!!!!!!")

            # Update the symbol character and position
            symbol.update()

            # Add fading effect in the column
            symbol.surface.set_alpha(i + (255 - (255 / self.column_height) * i))

            # Draw symbol to surface
            symbol.draw(surface)

        # Draw all placed symbols
        for symbol in self.placedSymbols:
            symbol.update()
            surface.blit(symbol.surface, (symbol.x, symbol.y))
