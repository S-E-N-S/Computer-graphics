import os, sys
import argparse


def main():
    # define command line arguments
    parser = argparse.ArgumentParser(description="shape_finder", add_help=True)

    parser.add_argument('-s', type=str, default="input.txt", dest="input_file", help="the input file name")
    parser.add_argument('-i', type=str, default="image.png", dest="image_file", help="the image file name")

    # parse command line arguments
    parsed_args = parser.parse_args()


if __name__ == "__main__":
    main()
