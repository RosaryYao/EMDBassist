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
import argparse
import base64
import math
import os
import struct
import sys

import mrcfile
import numpy as np


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


class Map:
    def __init__(self, fn):
        self.fn = fn
        self.mode, self.cols, self.rows, self.sections, self.data, self.origin, self.voxel_size = self._get_data(fn)

    def _get_data(self, fn):
        with mrcfile.open(fn) as mrc:
            mode = mrc.header.mode
            cols = mrc.header.nx
            rows = mrc.header.ny
            sections = mrc.header.nz
            origin = mrc.header.nxstart, mrc.header.nystart, mrc.header.nzstart
            voxel_size = mrc.voxel_size  # Would be a tuple?
            data = mrc.data
        return mode, cols, rows, sections, data, origin, voxel_size


class Tbl:
    def __init__(self, fn):
        self.fn = fn
        self.col, self.length, self.tbl_rows = self._get_data(fn)
        # Define a list of tbl_row

    def _get_data(self, fn):
        with open(fn, "r") as f:
            row_data = f.readlines()
            col_data = [row.strip().split(" ") for row in row_data]
            try:
                length_row = [len(row) for row in col_data]
                assert sum(length_row) / len(length_row) == length_row[0]
            except AssertionError:
                raise ValueError("Number of columns are not equal on all rows!")
        return len(col_data[0]), len(row_data), col_data

    def __setitem__(self, index, tbl_row):
        self.rows[index] = tbl_row

    def __getitem__(self, index):
        return self.tbl_rows[index]


class TblRow:
    def __init__(self, tbl_row, voxel_size = (1.0, 1.0, 1.0)):
        self.row = tbl_row
        self.size = voxel_size
        # change each element in the tbl_row into float
        self.dx, self.dy, self.dz, self.tdrot, self.tilt, self.narot, self.x, self.y, self.z = self._get_data(tbl_row)
        self.transformation = self._transform()


    def _get_data(self, tbl_row):
        dx, dy, dz = float(self.row[3]), float(self.row[4]), float(self.row[5])
        tdrot, tilt, narot = float(self.row[6]), float(self.row[7]), float(self.row[8])
        x, y, z = float(self.row[23]), float(self.row[24]), float(self.row[25])
        return dx, dy, dz, tdrot, tilt, narot, x, y, z

    # todo: Caution! Additional *self.size[i]. WHY???
    def _transform(self):
        rotation = rotate(math.radians(self.tdrot), math.radians(self.tilt), math.radians(self.narot))
        transformation = np.insert(rotation, 3, [(self.x + self.dx*self.size[0])*self.size[0],
                                                 (self.y + self.dy*self.size[0])*self.size[1],
                                                 (self.z + self.dz*self.size[0])*self.size[2]], axis=1)
        return transformation


class EM:
    """
    Dynamo produces subtomogram averaging volume data in .em format and stores binary data.
    See EMDB_mapFormat MODE at http://ftp.ebi.ac.uk/pub/databases/emdb/doc/Map-format/current/EMDB_map_format.pdf,
    After unpacking, the first number indicates the type of data. It is then followed by 3 numbers, denoting the numbers of columns, rows and sections.
    The rest is volume data.
    """

    def __init__(self, filename):
        self.filename = filename

        # todo: write a _get_data method
        with open(self.filename, 'rb') as em:
            # the header is 128 words = 512 bytes. np.dtype = "int32" (long integer)
            # we read the first 4 words (word = 4 bytes)
            self.dynamo_header = struct.unpack('128i', em.read(128 * 4))
            # determine the MODE
            self.dy_mode = int(hex(self.dynamo_header[0])[2])
            if self.dy_mode == 2:  # int16, short int
                self.mode = 1
                type_flag = "h"
            elif self.dy_mode == 4:  # int32, int
                self.mode = 3
                type_flag = "i"
            elif self.dy_mode == 5:  # float32
                self.mode = 2
                type_flag = "f"
            elif self.dy_mode == 9:  # float64
                self.mode = 4
                type_flag = "d"
            else:
                raise Exception("data not supported yet!")

            # pick the col, row, sect values
            self.nc, self.nr, self.ns = self.dynamo_header[1:4]
            # then we read the data
            self.raw_data = em.read()
            self.volume_data = struct.unpack(f'{self.nc * self.nr * self.ns}{type_flag}', self.raw_data)

    @property
    def volume_encoded(self):
        return base64.b64encode(self.raw_data)

    @property
    def volume_compressed(self):
        import zlib
        return zlib.compress(self.raw_data)

    @property
    def volume_encoded_compressed(self):
        return base64.b64encode(self.volume_compressed)

    @property
    def volume_array(self):
        import numpy
        return numpy.array(self.volume_data, dtype=numpy.float32).reshape(self.nc, self.nr, self.ns)


def create_output_files():
    args = parse_args()

    # Map information
    map = Map(args.map_file)
    map_origin = map.origin
    map_size = map.voxel_size.tolist()
    origin_m = np.array(
        [[0, 0, 0, map_origin[0]*map_size[0]], [0, 0, 0, map_origin[1]*map_size[1]], [0, 0, 0, map_origin[2]*map_size[2]]])

    # Tbl transformation
    tbl = Tbl(f"{args.data}.tbl")

    # .em data shape
    em = EM(f"{args.data}.em")
    box = em.volume_array.shape
    # Subtract half of the box_length
    half_box_m = np.array(
        [[0, 0, 0, (1/2)*box[0]*map_size[0]], [0, 0, 0, (1/2)*box[1]*map_size[1]], [0, 0, 0, (1/2)*box[2]*map_size[2]]])

    # A list contains the transformation of all particles
    transformations = []
    for i in range(tbl.length):
        tbl_row = TblRow(tbl[i], map_size)
        tbl_m = tbl_row.transformation
        transform_m = (tbl_m + origin_m - half_box_m)
        transformations.append(transform_m.tolist())

    # Output the text file
    with open(f"{args.data}_transformation.txt", "w") as f:
        for i in range(tbl.length):
            line_to_write = str(i + 1) + "," \
                            + "".join(
                str(f"{e},").replace("[", "").replace("]", "").replace(" ", "") for e in transformations[i]) \
                            + "0,0,0,1\n"
            f.write(line_to_write)

        f.write("Mode:" + "\t" + str(em.mode) + "\n")
        f.write("Nc:" + "\t" + str(em.nc) + "\n")
        f.write("Nr:" + "\t" + str(em.nr) + "\n")
        f.write("Ns:" + "\t" + str(em.ns) + "\n")

        output_flag = 0
        if args.compress:
            print('compressed')
            f.write(f"Data:\t{em.volume_encoded_compressed.decode('utf-8')}")
        else:
            print('uncompressed')
            f.write(f"Data:\t{em.volume_encoded.decode('utf-8')}")
            output_flag = 1

    if args.output:
        os.rename(rf"{args.data}_transformation.txt", rf"{args.output}.txt")
        output_flag = 2

    if output_flag == 2:
        print(f"{args.output}.txt" + " is created.")
    else:
        print(f"{args.data}_output.txt" + " is created.")

    if args.map_start:
        print("nxstart: " + str(map.origin[0]))
        print("nystart: " + str(map.origin[1]))
        print("nzstart: " + str(map.origin[2]))



def parse_args():
    # Argparse
    parser = argparse.ArgumentParser(
        description="output a single file that contains transformation data and voxel data. Default voxel data is "
                    "zlib compressed")
    parser.add_argument("-d", "--data", metavar="", required=True, help="the Dynamo .em and .tbl file.")
    # parser.add_argument("-t", "--tbl", default=False, action="store_true", help="the Dynamo .tbl file")
    parser.add_argument("-o", "--output", help="the output file name (.txt)")
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

    create_output_files()
    return 0


# only run main if this script is being executed
if __name__ == "__main__":
    # print(sys.argv)
    sys.exit(main())
