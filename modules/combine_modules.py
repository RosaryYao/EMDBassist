import transformation_dynamo as transform
import voxel_dynamo as voxel
import numpy
import os
import zlib
import base64
import argparse

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


def combine_data(em, tbl, output, flag_compress=True):
    with open(tbl, "rt") as tbl:
        # Create a list that contains all the transformations, and each transformation is treated as an element in the list
        # As well as rotations
        transformation_set = []
        polygon = [1, 1, 1]  # Just to make class Polygon works...
        length = 0

        for line in tbl:
            line = str(line).split(" ")
            transformation_string = ""

            # rotation in zxz convention; rotation angle in the corresponding order: a, b, c.
            a, b, c = float(line[6]), float(line[7]), float(line[8])
            rotation = transform.Polygon(polygon).rotate(a=a, b=b, c=c)
            rotation = rotation.tolist()
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
    em = voxel.EM(em)
    with open(f"{output}.txt", "w+") as file:
        for i in range(length):
            file.write("Tag, transformation:" + "\t" + str(i + 1) + "\t" + transformation_set[i] + "\n")

        file.write("Mode:" + "\t" + str(em.mode) + "\n")
        file.write("Nc:" + "\t" + str(em.nc) + "\n")
        file.write("Nr:" + "\t" + str(em.nr) + "\n")
        file.write("Ns:" + "\t" + str(em.ns) + "\n")

        if flag_compress:
            file.write(f"Data:\t{em.volume_encoded_compressed}")
            print(f"{output}_compressed.txt" + " is created.")
        elif flag_compress is False:
            file.write(f"Data:\t{em.volume_encoded}")
            print(f"{output}.txt" + " is created.")


def main():
    # Argparse
    global flag_compress
    parser = argparse.ArgumentParser(
        description="output a single file that contains transformation data and voxel data. Default voxel data is zlib compressed")
    parser.add_argument("-e", "--em", metavar="", required=True, help="the Dynamo .em file.")
    parser.add_argument("-t", "--tbl", metavar="", required=True, help="the Dynamo .tbl file")
    parser.add_argument("-o", "--output", metavar="", required=True, help="the output file name (.txt)")
    # Add compression flag - mutually exclusive group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--compress", action="store_true", help="Compress the voxel data")
    group.add_argument("-nc", "--not_compress", action="store_true",
                       help="Voxel data not compressed, in ascii encoded string")
    args = parser.parse_args()

    if args.compress:
        flag_compress = True
        # Output data with compressed raw_data, in binary
    elif args.not_compress:
        flag_compress = False
        # Output data in full ascii encoded data/string

    if not os.path.exists(args.em):
        raise ValueError(f"file '{args.em} does not exist")
    if not os.path.exists(args.tbl):
        raise ValueError(f"file '{args.tbl} does not exist")

    combine_data(args.em, args.tbl, args.output, flag_compress)


main()
