import math
import sys
import time

import cv2
import numpy as np
import pygame

from config import Config


class Image:

    def __init__(self, file_path):
        image = cv2.imread(file_path)

        if image is None:
            print(f"ERROR: Can't open image at: {file_path}")
            exit()

        if Config.SINGLE_COLOR_SELECTION:
            self.img_object = image

        # Do pre-processing if DRAW_LINES_OF_IMAGE is enabled
        elif Config.DRAW_LINES_OF_IMAGE:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            lines = cv2.Canny(image, 10, 200)

            contours = cv2.findContours(
                lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            contours = contours[0] if len(contours) == 2 else contours[1]

            for c in contours:
                cv2.drawContours(
                    lines, [c], -1, Config.ISOLATE_COLOR,
                    thickness=Config.LINE_THICKNESS
                )

            # Convert back from grayscale([0-255]) to rgb([0-255,0-255,0-255])
            self.img_object = cv2.cvtColor(lines, cv2.COLOR_GRAY2RGB)

            if Config.debug:
                cv2.imshow("Image converted", self.img_object)
                cv2.waitKey(0)

        self.path = file_path
        self.column_positions = {}

    def get_dimensions(self):
        y, x, _ = self.img_object.shape
        return x, y

    def get_centre(self):
        x, y = self.get_dimensions()
        return x / 2, y / 2

    def scale_image(self, scale_factor):
        x, y = self.get_dimensions()
        new_dimensions = (int(x * scale_factor), int(y * scale_factor))

        self.img_object = cv2.resize(
            self.img_object, new_dimensions, interpolation=cv2.INTER_AREA
        )

        if Config.debug:
            print(f"New dimensions: {new_dimensions}")

    def calculate_all_threshold_positions(self, size, color):
        # Apply mask to image
        if not Config.SINGLE_COLOR_SELECTION:
            color = (255, 255, 255)

        mask = cv2.inRange(self.img_object, color, color)

        if Config.debug:
            cv2.imshow("Masked image", mask)
            cv2.waitKey(0)

        # Code provided by
        # https://github.com/ilastik/lazyflow/blob/master/lazyflow/utility/blockwise_view.py,
        # an absolute god send

        # This compared to the other version is ~5000x faster
        # Breaks image down to sub matrices of size x size and then checks
        # if the mask has values
        block_shape = tuple((size, size))
        outer_shape = tuple(np.array(mask.shape) // block_shape)
        view_shape = outer_shape + block_shape

        if Config.debug:
            print(f"block shape: {block_shape}")
            print(f"outer shape: {outer_shape}")
            print(f"View shape: {view_shape}")

        # inner strides: strides within each block (same as original array)
        intra_block_strides = mask.strides

        # outer strides: strides from one block to another
        inter_block_strides = tuple(mask.strides * np.array(block_shape))

        # This is where the magic happens.
        # Generate a view with our new strides (outer+inner).
        sub_matrices = np.lib.stride_tricks.as_strided(
            mask, shape=view_shape, strides=(
                    inter_block_strides + intra_block_strides
            ))

        sub_len, sub_wid, _, _ = sub_matrices.shape

        # Loop through all sub matrices and
        for x in range(sub_wid - 1):
            y_positions = [
                y * size for y in range(sub_len - 1) if (
                    np.count_nonzero(sub_matrices[y][x]) / math.pow(size, 2)
                ) * 100 >= Config.THRESHOLD
            ]

            if y_positions:
                y_positions.sort(reverse=True)
                self.column_positions[x * size] = y_positions

    def translate_points_by_vector(self, vector):
        if self.column_positions == {}:
            print("Must calculate points to translate first")
            return

        vec_x, vec_y = vector

        self.column_positions = {
            xPos + vec_x: [yPos + vec_y for yPos in y_positions]
            for (xPos, y_positions) in self.column_positions.items()
        }

    def get_positions_for_column(self, column_pos):
        if self.column_has_positions(column_pos):
            return self.column_positions[column_pos]
        return []

    def columns_left_to_place(self):
        return any(
            self.column_has_positions(column) for column in self.get_columns()
        )

    def column_has_positions(self, column_pos):
        if column_pos in self.column_positions:
            return len(self.column_positions[column_pos]) > 0
        return False

    def get_next_position_for_column(self, column_num):
        return self.column_positions[column_num][0]

    def get_columns(self):
        return self.column_positions.keys()


def main():
    clock = pygame.time.Clock()
    pygame.display.set_caption("Image to font boxes calculated")

    # Open image and scale it
    img = Image(sys.argv[1])
    img.scale_image(Config.IMG_SCALE)

    width, length = img.get_dimensions()
    win = pygame.display.set_mode((width, length))

    start = time.time()
    img.calculate_all_threshold_positions(
        Config.FONT_SIZE, Config.ISOLATE_COLOR
    )

    finish = time.time()
    print(f"Finished calculating points in {finish - start} seconds")

    if not img.columns_left_to_place():
        print("Couldn't calculate any positions to draw")
        return

    stop_drawing = False
    is_running = True
    while is_running:

        if not stop_drawing:
            stop_drawing = True
            draw(win, img)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        pygame.display.update()
        clock.tick(Config.FADE_RATE)

    pygame.display.quit()
    pygame.quit()


def draw(win, img):
    white_square_size = (Config.FONT_SIZE, Config.FONT_SIZE)
    black_square_size = (Config.FONT_SIZE - 1, Config.FONT_SIZE - 1)

    for x, y_positions in img.column_positions.items():
        for y in y_positions:
            win.fill((0, 0, 0), pygame.Rect((x, y), white_square_size))
            win.fill((255, 255, 255), pygame.Rect((x, y), black_square_size))


if __name__ == "__main__":
    main()
