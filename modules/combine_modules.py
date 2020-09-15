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
# Consider combining? 
-----------Map information-------------------
EMDB map format
nc
nr
ns
volume_data (in string)
"""


def combine_data(em, tbl, output):
    with open(tbl, "rt") as tbl:
        # Create a list that contains all the transformations, and each transformation is treated as an element in the list
        # As well as rotations
        transformation_set = []
        polygon = [1, 1, 1]  # Just to make class Polygon works...
        length = 0

        for line in tbl:
            rotation_string = ""
            transformation = ""
            line = str(line).split(" ")
            vector = line[3] + "\t" + line[4] + "\t" + line[5]

            # rotation in zxz convension; rotation angle in the corresponding order: a, b, c.
            a, b, c = float(line[6]), float(line[7]), float(line[8])
            rotation = transform.Polygon(polygon).rotate(a=a, b=b, c=c)
            rotation = rotation.tolist()
            for row in rotation:
                for each in row:
                    rotation_string += (str(each) + "\t")
            rotation = rotation_string
            transformation = rotation + vector

            # print(transformation)
            transformation_set.append(transformation)
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
        file.write("Data:" + "\t" + str(em.volume_encoded))

    print(f"{output}.txt" + " is created.")

    # Compress data
    with open(f"{output}.txt", "r+") as file:
        # First encode into binary?
        file = str(file.read())
        file = file.encode("utf8")
        compressed_string = zlib.compress(file, level=9)
    with open(f"{output}_compressed.txt", "wb") as compressed:
        compressed.write(compressed_string)
        print("Compressed file is created.")
        # Did not compress much?


def main():
    # todo: consider using argparse library: https://docs.python.org/3/library/argparse.html
    # python my_script.py --em-file <path/file.em> --tbl-file <path/file.tbl>
    # python my_script.py <folder>
    # python my_script.py <prefix>
    # Argparse
    parser = argparse.ArgumentParser(description = "output a single file that contains transformation data and voxel data")
    parser.add_argument("-e", "--em", metavar="", required=True, help="the Dynamo .em file.")
    parser.add_argument("-t", "--tbl", metavar="", required=True, help="the Dynamo .tbl file")
    parser.add_argument("-o", "--output", metavar="", required=True, help="the output file name (.txt)")
    args = parser.parse_args()

    if not os.path.exists(args.em):
        raise ValueError(f"file '{args.em} does not exist")
    if not os.path.exists(args.tbl):
        raise ValueError(f"file '{args.tbl} does not exist")

    combine_data(args.em, args.tbl, args.output)
main()
