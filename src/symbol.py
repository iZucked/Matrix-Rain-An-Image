from random import choice, randrange
from typing import List

import pygame
from pygame.font import Font

from config import Config

NOT_PLACED = 0x00
PLACED = 0x01

pygame.init()

# Create our list of characters we can render which then is made in to a
# list of surfaces
font = pygame.font.Font(Config.FONT_PATH, Config.FONT_SIZE)


def get_char_surfaces(font: Font, char_set: List[chr], char_color: pygame.Color) -> List[pygame.Surface]:
    surfaces = []
    for char in char_set:
        try:
            surfaces.append(font.render(char, True, char_color))
        except pygame.error as e:
            # In case of 'Couldn't find glyph' error
            if "Couldn't find glyph" in e.args[0]:
                continue
    return surfaces


class Symbol:

    def __init__(self, x, y, speed, color):
        self.x, self.y = x, y
        self.speed = speed
        self.color = color

        self.interval = randrange(5, 30)
        self.state = NOT_PLACED

        self.charSet = get_char_surfaces(font, Config.CHARACTER_SET, color)
        self.surface = choice(self.charSet)

    def update(self):
        frames = pygame.time.get_ticks()

        if not frames % self.interval:
            self.surface = choice(self.charSet)

        if self.state == NOT_PLACED:
            self.y = self.y + self.speed \
                if self.y < Config.SCREEN_HEIGHT else -Config.FONT_SIZE

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

        self.speed = Config.FONT_SIZE if Config.RAIN_ACCUMULATION_MODE else (
            randrange(3, 8)
        )

        self.symbols = []
        self.placedSymbols = []
        self.placeable_positions = placeable_positions_list
        self.next_placement_pos = 0

        for n, i in enumerate(
                range(
                    start_y,
                    start_y - Config.FONT_SIZE * self.column_height,
                    -Config.FONT_SIZE
                )
        ):
            if n == 0:
                # Let first symbol be white
                self.symbols.append(
                    Symbol(pos_x, i, self.speed, pygame.Color('white'))
                )

            elif n % 2:
                self.symbols.append(
                    Symbol(pos_x, i, self.speed, (40, randrange(160, 256), 40))
                )

            else:
                self.symbols.append(
                    Symbol(pos_x, i, self.speed, pygame.Color('lightgreen'))
                )

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
            self.next_placement_pos = (
                self.placeable_positions.pop(0)
                if len(self.placeable_positions) > 0 else -1
            )

            self.place_white_symbol()

    def draw(self, surface):
        for i, symbol in enumerate(self.symbols):
            if symbol.state == PLACED:
                print(f"SYMBOL {symbol.x} should not be here!!!!!!!!!!!!")

            symbol.update()
            symbol.surface.set_alpha(i + (255 - (255 / self.column_height) * i))
            symbol.draw(surface)

        for symbol in self.placedSymbols:
            symbol.update()
            symbol.draw(surface)
