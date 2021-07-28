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
            self.imgObj = image
        # Do pre-processing if DRAW_LINES_OF_IMAGE is enabled
        elif Config.DRAW_LINES_OF_IMAGE:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            lines = cv2.Canny(image, 10, 200)
            white_px = np.where(lines == 255)
            cnts = cv2.findContours(
                lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            for c in cnts:
                cv2.drawContours(lines, [c], -1, Config.ISOLATE_COLOR,
                                 thickness=Config.LINE_THICKNESS)

            # Convert back from grayscale([0-255]) to rgb([0-255,0-255,0-255])
            self.imgObj = cv2.cvtColor(lines, cv2.COLOR_GRAY2RGB)

            if Config.debug:
                cv2.imshow("Image converted", self.imgObj)
                cv2.waitKey(0)

        self.path = file_path
        self.columnPositions = {}

    def get_dimensions(self):
        y, x, _ = self.imgObj.shape
        return x, y

    def get_centre(self):
        x, y = self.get_dimensions()
        return x / 2, y / 2

    def scale_image(self, scaleFactor):
        x, y = self.get_dimensions()
        new_dimensions = (int(x * scaleFactor), int(y * scaleFactor))
        self.imgObj = cv2.resize(self.imgObj, new_dimensions,
                                 interpolation=cv2.INTER_AREA)

        if Config.debug:
            print(f"New dimensions: {new_dimensions}")

    def calculate_all_threshold_positions(self, threshold, size, color):
        width, length = self.get_dimensions()

        # Apply mask to image
        if Config.SINGLE_COLOR_SELECTION:
            mask = cv2.inRange(self.imgObj, color, color)
        elif Config.DRAW_LINES_OF_IMAGE:
            mask = cv2.inRange(self.imgObj, (255, 255, 255), (255, 255, 255))

        if Config.debug:
            cv2.imshow("Masked image", mask)
            cv2.waitKey(0)

        # Code provided by
        # https://github.com/ilastik/lazyflow/blob/master/lazyflow/utility/blockwise_view.py,
        # an absolute god send

        # This compared to the other version is ~5000x faster
        # Breaks image down to submatracies of sizexsize and then checks if the
        # mask has values
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

        sub_len, subWid, _, _ = sub_matrices.shape

        # Loop through all sub matrices and
        for x in range(subWid - 1):
            y_positions = []
            for y in range(sub_len - 1):
                # Check if passes threshold occurances of color in submatrix
                n_occurrences = np.count_nonzero(sub_matrices[y][x])
                p_occurrences = (n_occurrences / math.pow(size, 2)) * 100
                if p_occurrences >= Config.THRESHOLD:
                    y_positions.append(y * size)
            if y_positions:
                y_positions.sort(reverse=True)
                self.columnPositions.update({x * size: y_positions})

    def translate_points_by_vector(self, vector):
        if self.columnPositions != {}:
            vec_x, vec_y = vector
            new_points = {}
            new_points = {
                xPos + vec_x: [yPos + vec_y for yPos in y_positions]
                for (xPos, y_positions) in self.columnPositions.items()
            }
            self.columnPositions = new_points
        else:
            print("Must calculate points to translate first")

    def get_positions_for_column(self, column_pos):
        if self.column_has_positions(column_pos):
            return self.columnPositions[column_pos]
        else:
            return []

    def columns_left_to_place(self):
        return any(
            self.column_has_positions(column) for column in self.get_columns()
        )

    def column_has_positions(self, column_pos):
        if column_pos in self.columnPositions:
            return len(self.columnPositions[column_pos]) > 0
        else:
            return False

    def get_next_position_for_column(self, column_num):
        return self.columnPositions[column_num][0]

    def get_columns(self):
        return self.columnPositions.keys()

    def get_num_columns(self):
        return len(self.columnPositions.keys())


def main():
    # Define clock for fps
    clock = pygame.time.Clock()

    # Set window title
    pygame.display.set_caption("Image to font boxes calculated")

    # Open image and scale it
    img = Image(sys.argv[1])
    img.scale_image(Config.IMG_SCALE)

    width, length = img.get_dimensions()
    win = pygame.display.set_mode((width, length))

    start = time.time()
    img.calculate_all_threshold_positions(
        Config.THRESHOLD, Config.FONT_SIZE, Config.ISOLATE_COLOR
    )
    finish = time.time()

    print(f"Finished calculating points in {finish - start} seconds")

    if not img.columns_left_to_place():
        print("Couldn't calculate any positions to draw")
        quit()

    stop_drawing = False

    while True:
        # Let clock tick
        clock.tick(Config.FADE_RATE)

        if not stop_drawing:
            stop_drawing = True

            for x, yPositions in img.columnPositions.items():
                for y in yPositions:
                    win.fill(
                        (0, 0, 0),
                        pygame.Rect(x, y, Config.FONT_SIZE, Config.FONT_SIZE)
                    )

                    win.fill(
                        (255, 255, 255),
                        pygame.Rect(
                            x, y, Config.FONT_SIZE - 1, Config.FONT_SIZE - 1
                        )
                    )

        # Getting events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        # Update frame
        pygame.display.update()


if __name__ == "__main__":
    main()
