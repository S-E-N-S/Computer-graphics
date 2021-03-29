import os, sys
import argparse
import cv2
import numpy as np

EPSILON = 2e-2


def read_patterns(patterns_file_name):
    with open(patterns_file_name) as patterns_file:
        patterns = []
        num_patterns = int(patterns_file.readline())
        for i in range(num_patterns):
            pattern_coords = list(map(int, patterns_file.readline().split(', ')))

            pattern_vtxes = np.array(pattern_coords).reshape((-1, 2))

            if cv2.contourArea(pattern_vtxes, True) < 0:
                pattern_vtxes = pattern_vtxes[::-1]

            patterns.append(pattern_vtxes)

        return patterns


def get_polygons(image):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    contours = np.array(contours)

    polygons = []
    for contour in contours:
        polygon = cv2.approxPolyDP(contour, EPSILON * cv2.arcLength(contour, True), True)
        polygons.append(np.squeeze(polygon, 1))
    return polygons


def get_angle(polygon, pattern):
    x_polygon, y_polygon = (polygon[1] - polygon[0]) / np.linalg.norm(polygon[1] - polygon[0])
    x_pattern, y_pattern = (pattern[1] - pattern[0]) / np.linalg.norm(pattern[1] - pattern[0])

    cos_angle = (x_polygon * x_pattern + y_polygon * y_pattern)
    rotation = np.arccos(cos_angle) * 180 / np.pi

    return [rotation - 1, rotation, rotation + 1]


def find_shift(polygon, pattern, scale, rotation):
    rotation = -rotation / 180 * np.pi

    x_polygon, y_polygon = polygon[0]
    x_pattern, y_pattern = pattern[0] * scale

    shift_x = x_polygon - (x_pattern * np.cos(rotation) - y_pattern * np.sin(rotation))
    shift_y = y_polygon - (x_pattern * np.sin(rotation) + y_pattern * np.cos(rotation))

    return shift_x, shift_y


def find_max_error(polygon, pattern, scale, rotation, shift_x, shift_y):
    rotation = -rotation / 180 * np.pi
    max_error = 0

    for polygon_vtx, pattern_vtx in zip(polygon, pattern):
        x_vtx, y_vtx = pattern_vtx * scale

        new_x = shift_x + (x_vtx * np.cos(rotation) - y_vtx * np.sin(rotation))
        new_y = shift_y + (x_vtx * np.sin(rotation) + y_vtx * np.cos(rotation))

        max_error = max(max_error, np.linalg.norm(polygon_vtx - (new_x, new_y)))

    return max_error


def get_sides(figure):
    sides = []
    for x, y in zip(figure[:-1], figure[1:]):
        sides.append(np.linalg.norm(x - y))
    sides.append(np.linalg.norm(figure[-1] - figure[0]))

    sides = np.array(sides)

    sides /= sides.sum()

    return sides


def find_objects(patterns, polygons):
    obgects = []
    for polygon in polygons:
        poly_sides = get_sides(polygon)
        match_error = np.inf
        for j, pattern in enumerate(patterns):
            pattern_sides = get_sides(pattern)
            if polygon.shape[0] == pattern.shape[0]:

                # find possible match of pattern/polygon
                possible_match = []
                pattern_copy = pattern.copy()
                for _ in range(polygon.shape[0]):
                    if np.linalg.norm(pattern_sides - poly_sides) < EPSILON:
                        possible_match.append(polygon.copy())
                        break
                    pattern_sides = np.roll(pattern_sides, 1, 0)
                    pattern_copy = np.roll(pattern_copy, 1, 0)

                for match in possible_match:
                    scale = np.round(np.sqrt(cv2.contourArea(match) / cv2.contourArea(pattern_copy))).astype(int)
                    angles = np.round(get_angle(match, pattern_copy)).astype(int)

                    for rotation in angles:
                        shift_x, shift_y = np.round(find_shift(match,
                                                               pattern_copy,
                                                               scale,
                                                               rotation)
                                                    ).astype(int)

                        max_match_error = find_max_error(match,
                                                         pattern_copy,
                                                         scale,
                                                         rotation,
                                                         shift_x,
                                                         shift_y)
                        if max_match_error < match_error:
                            match_error = max_match_error
                            pattern_num, min_shift_x, min_shift_y, min_scale, min_rotation = j, shift_x, shift_y, scale, rotation

        if match_error < np.inf:
            obgects.append([pattern_num,
                            min_shift_x,
                            min_shift_y,
                            min_scale,
                            min_rotation])

    return np.round(obgects).astype(int)


def main():
    # define command line arguments
    parser = argparse.ArgumentParser(description="shape_finder", add_help=True)

    parser.add_argument('-s', type=str, default="input.txt", dest="input_file", help="the input file name")
    parser.add_argument('-i', type=str, default="image.png", dest="image_file", help="the image file name")

    # parse command line arguments
    parsed_args = parser.parse_args()

    patterns = read_patterns(parsed_args.patterns_file_name)

    image = cv2.imread(parsed_args.image_name, cv2.IMREAD_GRAYSCALE)

    polygons = get_polygons(image)

    objects = find_objects(patterns, polygons)

    print(objects.shape[0])
    for object in objects:
        print(*object, sep=', ')


if __name__ == "__main__":
    main()
