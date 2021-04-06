import argparse
import numpy as np
#from shape_finder import read_patterns
from TestGenerator import Transform
import cv2
from matplotlib import pyplot as plt

def read_patterns(patterns_file_name):
    with open(patterns_file_name) as patterns_file:
        patterns = []
        num_patterns = int(patterns_file.readline())
        for i in range(num_patterns):
            pattern_coords = list(map(int, patterns_file.readline().split(', ')))

            # pattern_vtxes = np.flip(np.array(pattern_coords).reshape((-1, 2)), axis=1)
            pattern_vtxes = np.array(pattern_coords).reshape((-1, 2))
            patterns.append(pattern_vtxes)

    return patterns


def IoU(img1, img2):
    inter = img1 & img2
    union = img1 | img2
    inter = float(np.count_nonzero(inter > 0))
    union = float(np.count_nonzero(union > 0))
    return inter / union


def read_answers(output_file):
    with open(output_file) as file:
        figures_params = []  # list of pairs (pattern id, Transform)
        num_figures = int(file.readline())
        for i in range(num_figures):
            figures_param_list = list(map(int, file.readline().split(', ')))
            if len(figures_param_list) != 5:
                raise RuntimeError(f'wrong format of {output_file}')
            figures_params.append((figures_param_list[0],
                                  Transform({
                                      'dx': figures_param_list[1],
                                      'dy': figures_param_list[2],
                                      'scale': figures_param_list[3],
                                      'angle': figures_param_list[4]
                                  })))

    return figures_params


def draw_result(input_file, output_file):
    patterns = read_patterns(input_file)
    fig_params = read_answers(output_file)
    im_shape = (200, 300)
    color = 255  # white
    predict_image = np.zeros(shape=im_shape, dtype=np.int32)
    for fig_id, transform in fig_params:
        shape = patterns[fig_id]
        new_shape = shape.copy().astype(float)
        # Scale
        new_shape *= transform.scale

        # Rotation
        tmp = new_shape.copy()
        for i in [0, 1]:
            new_shape[:, i] = np.cos(transform.angle) * tmp[:, i] \
                              - ((-1) ** i) * np.sin(transform.angle) * tmp[:, i-1]

        # Shift
        new_shape[:, 0] += transform.dx
        new_shape[:, 1] += transform.dy

        cv2.fillPoly(predict_image, [new_shape.astype(np.int32)], color)
    plt.imsave("tmp.png", predict_image, cmap='gray')
    return predict_image


def main():
    # define command line arguments
    parser = argparse.ArgumentParser(description="shape_finder", add_help=True)

    parser.add_argument('-s', type=str, default="000_line_in.txt", dest="patterns_file_name", help="patterns")
    parser.add_argument('-a', type=str, default="out.txt", dest="model_ans_file", help="the answers of the model")
    parser.add_argument('-g', type=str, default="000_line_gt.png", dest="ground_truth", help="the ground truth image")

    # parse command line arguments
    parsed_args = parser.parse_args()

    predict_image = draw_result(parsed_args.patterns_file_name, parsed_args.model_ans_file)
    predict_image = predict_image > 128
    ground_truth = cv2.imread(parsed_args.ground_truth, cv2.IMREAD_GRAYSCALE) > 128

    print(IoU(predict_image, ground_truth))


if __name__ == "__main__":
    main()
