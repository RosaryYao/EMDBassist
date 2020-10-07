import argparse
import math
import os
import sys
import mrcfile

import numpy as np
import voxel_dynamo as voxel

"""
.tbl field values (1-based index)
https://wiki.dynamo.biozentrum.unibas.ch/w/index.php/Table_convention
1  : tag tag of particle file in data folder
2  : aligned value 1: marks the particle for alignment
3  : averaged value 1: the particle was included in the average
4  : dx x shift from center (in pixels)
5  : dy y shift from center (in pixels)
6  : dz z shift from center (in pixels)
7  : tdrot euler angle (rotation around z, in degrees)
8  : tilt euler angle (rotation around new x, in degrees)
9  : narot euler angle (rotation around new z, in degrees)
10  : cc Cross correlation coefficient
11  : cc2 Cross correlation coefficient after thresholding II
12  : cpu processor that aligned the particle
13  : ftype 0: full range; 1: tilt around y ( ... dhelp dtutorial for more options)
14  : ymintilt minimum angle in the tilt series around tilt axis (i.e. -60)
15  : ymaxtilt maximum angle in the tilt series around tilt axis (i.e. 60)
16  : xmintilt minimum angle in the tilt series around second tilt axis (i.e. -60)
17  : xmaxtilt maximum angle in the tilt series around second x (i.e. 60)
18  : fs1 free parameter for fourier sampling #1()
19  : fs2 free parameter for fourier sampling #2()
20  : tomo tomogram number
21  : reg for arbitrary assignations of regions inside tomograms
22  : class class number
23  : annotation use this field for assigning arbitrary labels
24  : x x coordinate in original volume
25  : y y coordinate in original volume
26  : z z coordinate in original volume
27  : dshift norm of shift vector
28  : daxis difference in axis orientation
29  : dnarot difference in narot
30  : dcc difference in CC
31  : otag original tag (subboxing)
32  : npar number of added particles (compactions) / subunit label (subboxing)
34  : ref reference. Used in multireference projects
35  : sref subreference (i.e. generated by Dynamo PCA)
36  : apix angstrom per pixel
37  : def defocus (in micron)
41  : eig1 "eigencoefficient" #1
42  : eig2 "eigencoefficient" #2
"""


# Define rotation matrices (anticlockwise)
def matrix_z(theta):
    matrix = np.array([
        [math.cos(theta), math.sin(theta), 0],
        [-math.sin(theta), math.cos(theta), 0],
        [0, 0, 1]
    ])
    return matrix


def matrix_y(theta):
    matrix = np.array([
        [math.cos(theta), 0, -math.sin(theta)],
        [0, 1, 0],
        [math.sin(theta), 0, math.cos(theta)]
    ])
    return matrix


def matrix_x(theta):
    matrix = np.array([
        [1, 0, 0],
        [0, math.cos(theta), math.sin(theta)],
        [0, -math.sin(theta), math.cos(theta)]
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

    ## Define <file_root> - if .tbl and .em has the same file_root.
    ## Also assume output start has the same root unless stated
    # file_root = os.path.splitext(args.em)[0]

    """
    todo: replace all below with something like this
    map_obj = MAP(args.map_file)
    map_obj.nxstart ...
    map_obj.voxel_size_x ...
    """
    with mrcfile.open(args.map_file) as mrc:
        header = mrc.header
        voxel_size = mrc.voxel_size
        vx = voxel_size.x
        vy = voxel_size.y
        vz = voxel_size.z

        nxstart = float(header.nxstart)
        nystart = float(header.nystart)
        nzstart = float(header.nzstart)
        start_list = [nxstart, nystart, nzstart]
        print(f"start_list: {start_list}")

        # Print nxstart, nystart and nzstart of the original .map file
        if args.map_start:
            print("nxstart: " + str(header.nxstart))
            print("nystart: " + str(header.nystart))
            print("nzstart: " + str(header.nzstart))

    print(f"vx = {vx}")
    print(f"vy = {vy}")
    print(f"vz = {vz}")

    # Consider box size - half of the volume shape
    """
    todo: use the em object for attributes
    """
    # fixme: add args to voxel.EM
    em = voxel.EM(f"{args.data}.em")
    # fixme: no need to create a     new variable
    volume_shape = em.volume_array.shape  # This is a tuple
    print("Volume shape: " + str(volume_shape))

    """
    todo: create a class that handles .tbl files just as with .em files
    # class for the file
    tbl = TBL('file.tbl', args)
    len(tbl) # number of particles

    #for each row we also need a class
    class TBLRow:
        pass

    tbl_row = tbl[1] # returns a TBLRow object with tag = 1 
    # attributes with names according to Dynamo e.g. 
    tbl_row.tdrot
    tbl_row.tilt
    tbl_row.narot
    # method on TBLRow
    tbl_row.transform #property -> 4x4 matrix
    """
    with open(f"{args.data}.tbl", "rt") as tbl:
        # Create a list that contains all the transformations,
        # and each transformation is treated as an element in the list
        transformation_set = []
        length = 0

        for line in tbl:
            line = str(line).split(" ")
            transformation_string = ""

            ds = [float(line[3]) * vx, float(line[4]) * vy, float(line[5]) * vz]

            # rotation in zxz convention; rotation angle in the corresponding order: a, b, c.
            a, b, c = math.radians(float(line[6])), math.radians(float(line[7])), math.radians(float(line[8]))
            ## d = float(line[29])
            ## a = math.radians(a + d)
            # Call the function
            rotation = rotate(a, b, c)

            flag = 23
            s_flag = 0

            # todo: CHECK!!!!!
            random_values = [5, 5, 5]
            voxel_size_list = [vx, vy, vz]
            for row in rotation:
                rotation_string = ""
                for each in row:
                    rotation_string += (str(each) + ",")
                # *voxel_size_list[s_flag]
                #
                translation = (float(line[flag]) + float(start_list[s_flag]) + ds[s_flag] - volume_shape[s_flag] / 2) * \
                              voxel_size_list[s_flag]
                transformation = rotation_string + str(translation) + ","
                transformation_string += transformation
                flag += 1
                s_flag += 1

            transformation_set.append(transformation_string)
            length += 1

    # Output the final text file

    # todo: create a function for output
    # write_output(args)
    with open(f"{args.data}_output.txt", "w+") as file:
        for i in range(length):
            # fixme: make sure that transformation_set[i] does not have \t at the end
            line_to_write = str(i + 1) + "," + transformation_set[i][:-1] + ",0,0,0,1\n"
            file.write(line_to_write)

        file.write("Mode:" + "\t" + str(em.mode) + "\n")
        file.write("Nc:" + "\t" + str(em.nc) + "\n")
        file.write("Nr:" + "\t" + str(em.nr) + "\n")
        file.write("Ns:" + "\t" + str(em.ns) + "\n")

        output_flag = 0
        if args.compress:
            print('compressed')
            file.write(f"Data:\t{em.volume_encoded_compressed.decode('utf-8')}")
        else:
            print('uncompressed')
            file.write(f"Data:\t{em.volume_encoded.decode('utf-8')}")
            output_flag = 1

    if args.output != "":
        os.rename(rf"{args.data}_output.txt", rf"{args.output}.txt")
        output_flag = 2

    if output_flag == 2:
        print(f"{args.output}.txt" + " is created.")
    else:
        print(f"{args.data}_output.txt" + " is created.")

    # todo: create a function to write out mrc
    with mrcfile.new(f"{args.data}.mrc", overwrite=True) as m:
        m.set_data(em.volume_array)
        m.voxel_size = 5.43


def parse_args():
    # Argparse
    parser = argparse.ArgumentParser(
        description="output a single file that contains transformation data and voxel data. Default voxel data is "
                    "zlib compressed")
    parser.add_argument("-d", "--data", metavar="", required=True, help="the Dynamo .em and .tbl file.")
    # parser.add_argument("-t", "--tbl", default=False, action="store_true", help="the Dynamo .tbl file")
    parser.add_argument("-o", "--output", default="", help="the output file name (.txt)")
    parser.add_argument("-c", "--compress", default=False, action="store_true",
                        help="Compress the voxel data [default: False]")
    parser.add_argument("-m", "--map-file", metavar="", help="The original .map file")
    parser.add_argument("-s", "--map-start", default=False, action="store_true",
                        help="Print the nxstart, nystart, nzstart of the original .map file")
    args, unknown = parser.parse_known_args()
    return args


def main():
    args = parse_args()

    if not os.path.exists(f"{args.data}.em"):
        raise ValueError(f"file '{args.data}.em does not exist")
    if not os.path.exists(f"{args.data}.tbl"):
        raise ValueError(f"file '{args.data}.tbl does not exist")

    combine_data(args)
    return 0


# only run main if this script is being executed
if __name__ == "__main__":
    # print(sys.argv)
    sys.exit(main())