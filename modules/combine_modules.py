import argparse
import math
import os
import sys

import numpy as np
import voxel_dynamo as voxel


# Define rotation matrices (anticlockwise)
def matrix_z(theta):
    matrix = np.array([
        [math.cos(theta), -math.sin(theta), 0],
        [math.sin(theta), math.cos(theta), 0],
        [0, 0, 1]
    ])
    return matrix


def matrix_y(theta):
    matrix = np.array([
        [math.cos(theta), 0, math.sin(theta)],
        [0, 1, 0],
        [-math.sin(theta), 0, math.cos(theta)]
    ])
    return matrix


def matrix_x(theta):
    matrix = np.array([
        [1, 0, 0],
        [0, math.cos(theta), -math.sin(theta)],
        [0, math.sin(theta), math.cos(theta)]
    ])
    return matrix


def rotate(a, b, c, convention="zxz"):
    """
    Rotation uses Euler angles. 6 conventions exist: "zxz", "zyz", "xzx", "xyx", "yxy", "yzy". Default is "zxz" convention.
    Rotation here is anticlockwise, since Dynamo rotates objects in clockwise direction.
    """

    if convention == "zxz":
        return matrix_z(a).dot(matrix_x(b)).dot(matrix_z(c))
    elif convention == "zyz":
        return matrix_z(a).dot(matrix_y(b)).dot(matrix_z(c))
    elif convention == "yzy":
        return matrix_y(a).dot(matrix_z(b)).dot(matrix_y(c))
    elif convention == "yxy":
        return matrix_y(a).dot(matrix_x(b)).dot(matrix_y(c))
    elif convention == "xzx":
        return matrix_x(a).dot(matrix_z(b)).dot(matrix_x(c))
    elif convention == "xyx":
        return matrix_x(a).dot(matrix_y(b)).dot(matrix_x(c))
    else:
        print("convention not supported")

    return


def combine_data(args):
    """
    The output format:
    -----------Transformation data--------------
    (translation vector + "\t" + rotation matrix)*n
    -----------Map information-------------------
    EMDB map format
    nc
    nr
    ns
    volume_data (in string)
    """
    with open(args.tbl, "rt") as tbl:
        # Create a list that contains all the transformations,
        # and each transformation is treated as an element in the list
        transformation_set = []
        length = 0

        for line in tbl:
            line = str(line).split(" ")
            transformation_string = ""

            # rotation in zxz convention; rotation angle in the corresponding order: a, b, c.
            a, b, c = float(line[6]), float(line[7]), float(line[8])
            # Call the function
            rotation = rotate(a, b, c)

            flag = 3
            for row in rotation:
                rotation_string = ""
                for each in row:
                    rotation_string += (str(each) + "\t")
                transformation = rotation_string + line[flag] + "\t"
                transformation_string += transformation
                flag += 1

            transformation_set.append(transformation_string)
            length += 1

    # Output the final text file
    em = voxel.EM(args.em)
    with open(f"{args.output}.txt", "w+") as file:
        for i in range(length):
            file.write("Tag, transformation:" + "\t" + str(i + 1) + "\t" + transformation_set[i] + "\n")

        file.write("Mode:" + "\t" + str(em.mode) + "\n")
        file.write("Nc:" + "\t" + str(em.nc) + "\n")
        file.write("Nr:" + "\t" + str(em.nr) + "\n")
        file.write("Ns:" + "\t" + str(em.ns) + "\n")

        if args.compress:
            print('compressed')
            file.write(f"Data:\t{em.volume_encoded_compressed.decode('utf-8')}")
            print(f"{args.output}_compressed.txt" + " is created.")
        else:
            print('uncompressed')
            file.write(f"Data:\t{em.volume_encoded.decode('utf-8')}")
            print(f"{args.output}.txt" + " is created.")


def main():
    # Argparse
    parser = argparse.ArgumentParser(
        description="output a single file that contains transformation data and voxel data. Default voxel data is "
                    "zlib compressed")
    parser.add_argument("-e", "--em", metavar="", required=True, help="the Dynamo .em file.")
    parser.add_argument("-t", "--tbl", metavar="", required=True, help="the Dynamo .tbl file")
    parser.add_argument("-o", "--output", metavar="", required=True, help="the output file name (.txt)")
    parser.add_argument("-c", "--compress", default=False, action="store_true",
                        help="Compress the voxel data [default: False]")
    args = parser.parse_args()

    if not os.path.exists(args.em):
        raise ValueError(f"file '{args.em} does not exist")
    if not os.path.exists(args.tbl):
        raise ValueError(f"file '{args.tbl} does not exist")

    combine_data(args)
    return 0


# only run main if this script is being executed
if __name__ == "__main__":
    sys.exit(main())
