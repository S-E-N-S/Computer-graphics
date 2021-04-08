import sys
import argparse
import cv2
import numpy as np
#from matplotlib import pyplot as plt

EPSILON = 2e-2


def read_patterns(patterns_file_name):
    with open(patterns_file_name) as patterns_file:
        patterns = []
        orient = []
        num_patterns = int(patterns_file.readline())
        for i in range(num_patterns):
            pattern_coords = list(map(int, patterns_file.readline().split(', ')))

            # pattern_vtxes = np.flip(np.array(pattern_coords).reshape((-1, 2)), axis=1)
            pattern_vtxes = np.array(pattern_coords).reshape((-1, 2))

            if cv2.contourArea(pattern_vtxes, True) < 0:
                pattern_vtxes = pattern_vtxes[::-1]
                pattern_vtxes = np.roll(pattern_vtxes, 1, 0)
                orient.append(-1)
            else:
                orient.append(1)

            patterns.append(pattern_vtxes)

    return patterns, orient


def binarize_image(image):
    im_cpy = image.copy()
    im_cpy[im_cpy > 0] = 1
    return im_cpy


def remove_lines(image):
    im_cpy = image.copy()
    kernel_size = 3
    # define line ending patterns
    # this is needed to remove noise or separate lines
    # we use the fact each line has the same width == 1 pixel
    # we use the fact each polygon line has no "pure" end (the line end is the corner)
    # so the patterns defined below can help detect extra line endings
    # and the line ending will be always at the center of each pattern
    ending_filters = np.array([
        [[0, 1, 0],  # pattern 1
         [0, 1, 0],
         [0, 0, 0]],
        [[0, 0, 0],  # pattern 2
         [0, 1, 0],
         [0, 1, 0]],
        [[0, 0, 0],  # pattern 3
         [1, 1, 0],
         [0, 0, 0]],
        [[0, 0, 0],  # and so on...
         [0, 1, 1],
         [0, 0, 0]],
        [[0, 0, 1],
         [0, 1, 0],
         [0, 0, 0]],
        [[0, 0, 0],
         [0, 1, 0],
         [1, 0, 0]],
        [[1, 0, 0],
         [0, 1, 0],
         [0, 0, 0]],
        [[0, 0, 0],
         [0, 1, 0],
         [0, 0, 1]],
        [[0, 0, 0],
         [0, 1, 0],
         [0, 0, 0]]
    ])
    ax_1, ax_2 = image.shape
    # we will remove line endings until we can't
    not_stopped = True
    iters, max_iters = 0, 100  # iterations limit
    bias_to_center = kernel_size // 2  # bias to get the center of the sliding window
    while not_stopped and iters < max_iters:
        iters += 1
        not_stopped = False  # stop if there will be no changes
        for start_coord_1 in range(ax_1 - kernel_size + 1):
            for start_coord_2 in range(ax_2 - kernel_size + 1):
                # get current area
                cur_area = im_cpy[start_coord_1:start_coord_1 + kernel_size,
                                  start_coord_2:start_coord_2 + kernel_size]
                if np.all(cur_area == 0):
                    # optimization: don't compare not interesting areas
                    continue
                # check area borders
                for f_num in range(ending_filters.shape[0]):
                    if np.all(cur_area == ending_filters[f_num, :, :]):
                        not_stopped = True  # change image => may try once more
                        # matches template
                        # erase line ending with 0
                        im_cpy[start_coord_1 + bias_to_center,
                               start_coord_2 + bias_to_center] = 0
    return im_cpy


def get_polygons(image):
    # firstly, binarize image (all non-zero intensities will be set to 1)
    image = binarize_image(image)
    # remove noise and extra lines
    image = remove_lines(image)
    # show the result of de-noising
    #plt.imshow(image, cmap='gray')
    #plt.imsave("better.png", image, cmap='gray')
    #plt.show()

    # find contours on denoised image
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = np.array(contours)

    polygons = []
    for contour in contours:
        polygon = cv2.approxPolyDP(contour, EPSILON * cv2.arcLength(contour, True), True)
        polygon = np.squeeze(polygon, 1)
        if cv2.contourArea(polygon, True) < 0:
            polygon = polygon[::-1]

        polygons.append(polygon)

    return polygons


def get_angle(polygon, pattern):
    x_polygon, y_polygon = (polygon[1] - polygon[0]) / np.linalg.norm(polygon[1] - polygon[0])
    x_pattern, y_pattern = (pattern[1] - pattern[0]) / np.linalg.norm(pattern[1] - pattern[0])

    cos_angle = (x_polygon * x_pattern + y_polygon * y_pattern)
    rotation = np.arccos(cos_angle) * 180 / np.pi

    return [rotation - 1, rotation, rotation + 1]


def find_max_error(polygon, pattern, scale, rotation, shift_x, shift_y):
    rotation = rotation / 180 * np.pi
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


def find_objects(patterns, polygons, orient):
    objects = []
    for polygon in polygons:
        poly_sides = get_sides(polygon)
        match_error = np.inf
        for j, pattern in enumerate(patterns):
            pattern_sides = get_sides(pattern)
            if polygon.shape[0] == pattern.shape[0]:
                # find possible match of pattern/polygon
                possible_match = []
                sides = poly_sides.copy()
                polygon_copy = polygon.copy()
                for _ in range(polygon_copy.shape[0]):
                    if np.linalg.norm(pattern_sides - sides) < EPSILON:
                        possible_match.append(polygon_copy.copy())

                    sides = np.roll(sides, 1, 0)
                    polygon_copy = np.roll(polygon_copy, 1, 0)

                scale = np.round(np.sqrt(cv2.contourArea(polygon_copy) / cv2.contourArea(pattern))).astype(int)
                pattern_num = j

                for match in possible_match:

                    angles = - np.round(get_angle(match, pattern)).astype(int) * orient[j]

                    shift_x, shift_y = match[0].copy()

                    for rotation in angles:
                        max_match_error = find_max_error(match,
                                                         pattern,
                                                         scale,
                                                         rotation,
                                                         shift_x,
                                                         shift_y)
                        if max_match_error < match_error:
                            match_error = max_match_error
                            min_rotation = rotation
                            min_shift_x, min_shift_y = shift_x, shift_y

        if match_error < np.inf:
            objects.append([pattern_num,
                            min_shift_x,
                            min_shift_y,
                            scale,
                            min_rotation])

    return np.round(objects).astype(int)


def main():
    # define command line arguments
    parser = argparse.ArgumentParser(description="shape_finer", add_help=True)

    parser.add_argument('-s', type=str, default="000_line_in.txt", dest="patterns_file_name", help="the input file name")
    parser.add_argument('-i', type=str, default="000_pure_src.png", dest="image_name", help="the image file name")
    parser.add_argument('-o', type=str, default="", dest="outfile", help="the output file name")

    # parse command line arguments
    parsed_args = parser.parse_args()

    patterns, orient = read_patterns(parsed_args.patterns_file_name)

    image = cv2.imread(parsed_args.image_name, cv2.IMREAD_GRAYSCALE)

    polygons = get_polygons(image)

    objects = find_objects(patterns, polygons, orient)

    outfile = sys.stdout
    if parsed_args.outfile != "":
        outfile = open(parsed_args.outfile, 'w')
        need_close = True
    else:
        need_close = False

    print(objects.shape[0], file=outfile)
    for obj in objects:
        print(*obj, sep=', ', file=outfile)
    if need_close:
        outfile.close()


if __name__ == "__main__":
    main()
