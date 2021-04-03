import argparse


def main():
    # define command line arguments
    parser = argparse.ArgumentParser(description="shape_finder", add_help=True)

    parser.add_argument('-s', type=str, default="input.txt", dest="patterns_file_name", help="patterns")
    parser.add_argument('-a', type=str, default="output.txt", dest="model_ans_file", help="the answers of the model")
    parser.add_argument('-g', type=str, default="im_gt.png", dest="ground_truth", help="the ground truth image")

    # parse command line arguments
    parsed_args = parser.parse_args()


if __name__ == "__main__":
    main()
