import cv2
import numpy as np
from matplotlib import pyplot as plt


class Transform:
    def __init__(self, obj):
        self.scale = obj['scale'] if 'scale' in obj else 1
        self.angle = obj['angle'] * np.pi / 180.0 if 'angle' in obj else 0
        self.dx = obj['dx'] if 'dx' in obj else 0
        self.dy = obj['dy'] if 'dy' in obj else 0


def draw(input_image, ground_truth, shape, transform: Transform, color=255):
    assert (input_image.shape == ground_truth.shape)

    new_shape = shape.copy().astype(float)
    # Scale
    new_shape *= transform.scale

    # Rotation
    tmp = new_shape.copy()
    for i in [0, 1]:
        new_shape[:, i] = np.cos(transform.angle) * tmp[:, i] \
                          - ((-1) ** i) * np.sin(transform.angle) * tmp[:, 1 - i]

    # Shift
    new_shape[:, 0] += transform.dx
    new_shape[:, 1] += transform.dy

    # gt fill with polygon edges
    cv2.fillPoly(ground_truth, [new_shape.astype(np.int32)], color)
    cv2.polylines(input_image, [new_shape.astype(np.int32)], True, color)


def get_shapes():
    triangle_1 = np.array([[0, 0],
                           [1, 1],
                           [1, 0]])
    triangle_2 = np.array([[0, 0],
                           [2, 1],
                           [1, 0]])
    square = np.array([[0, 0],
                       [0, 1],
                       [1, 1],
                       [1, 0]])

    return [triangle_1, triangle_2, square]


def get_transforms(im_shape, h_cnt, w_cnt):
    step_h = im_shape[0] / (h_cnt + 1)
    step_w = im_shape[1] / (w_cnt + 1)
    shift_h = step_h / 2
    shift_w = step_w / 2
    scale_min = min(step_h, step_w) / 4
    scale_max = min(step_h, step_w) / 2
    for cur_h in range(h_cnt):
        for cur_w in range(w_cnt):
            scale = np.random.uniform(low=scale_min, high=scale_max)
            dx, dy = np.random.uniform(low=[shift_w + step_w * cur_w + scale, shift_h + step_h * cur_h + scale],
                                       high=[shift_w + step_w * (cur_w + 1) - scale, shift_h + step_h
                                             * (cur_h + 1) - scale])
            angle = np.random.uniform(low=0, high=179)
            transform = {
                'scale': scale,
                'angle': angle,
                'dx': dx,
                'dy': dy
            }
            yield transform


def generate_image(outfile, outfile_txt, infile_txt):
    im_shape = (200, 300)
    input_img = np.zeros(shape=im_shape, dtype=np.int32)
    ground_truth = input_img.copy()
    shapes = get_shapes()
    worklist = []  # output.txt ground truth
    for transform in get_transforms(im_shape, 1, 1):
        cur_shape = int(np.round(np.random.uniform(low=0, high=len(shapes) - 1)))
        draw(input_img, ground_truth, shapes[cur_shape], Transform(transform))
        worklist.append([cur_shape, transform['dx'], transform['dy'], transform['scale'],
                         transform['angle']])
    # save images
    plt.imsave(outfile + '.png', input_img, cmap='gray')
    plt.imsave(outfile + '_gt.png', ground_truth, cmap='gray')
    # save output.txt ground truth
    separator = ', '
    with open(outfile_txt, 'w') as file:
        print(f"{len(worklist)}", file=file)
        for ans in worklist:
            line = separator.join([str(int(cur)) for cur in ans])
            print(line, file=file)
    # save input.txt file
    with open(infile_txt, 'w') as file:
        print(f"{len(shapes)}", file=file)
        for shape in shapes:
            coord_list = shape.flatten().tolist()
            print(separator.join([str(int(cur)) for cur in coord_list]), file=file)


def main():
    generate_image('in_image', 'out_gen.txt', 'in.txt')


if __name__ == "__main__":
    main()
