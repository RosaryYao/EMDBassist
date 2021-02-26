import math
import struct

import numpy as np

from . import TableBase


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


class TableRow:
    def __init__(self, motl_row, voxel_size=(1.0, 1.0, 1.0)):
        self.row = motl_row
        # change each element in the tbl_row into float
        self.dx, self.dy, self.dz, self.tdrot, self.tilt, self.narot, \
        self.x, self.y, self.z = self._get_data()
        self.transformation = self._transform()

    def _get_data(self):
        dx, dy, dz = float(self.row[10]), float(self.row[11]), float(self.row[12])  # todo: fix here
        # if dx != 0 or dy != 0 or dz != 0:
        #    raise ValueError("shifts in x, y, z are note equal to zero")

        tdrot, tilt, narot = math.radians(float(self.row[17])), math.radians(float(self.row[18])), math.radians(
            float(self.row[16]))
        x, y, z = float(self.row[7] + dx), float(self.row[8] + dy), float(self.row[9] + dz)
        return dx, dy, dz, tdrot, tilt, narot, x, y, z

    def _transform(self):
        matrix_z_inv = np.linalg.inv(matrix_z(self.tdrot))
        matrix_x_inv = np.linalg.inv(matrix_x(self.tilt))
        matrix_z_inv_2 = np.linalg.inv(matrix_z(self.narot))
        rotation = matrix_z_inv.dot(matrix_x_inv).dot(matrix_z_inv_2)
        # rotation = rotate(math.radians(self.tdrot), math.radians(self.tilt), math.radians(self.narot))

        translation = np.array(
            [self.x,
             self.y,
             self.z]
        )
        np.set_printoptions(suppress=True)  # To suppress scientific notation
        transformation = np.insert(rotation, 3, translation, axis=1)
        return transformation

    def __str__(self):
        string = "".join(f"{str(e)}," for e in self.transformation.flatten())
        line_to_write = string + "0,0,0,1\n"
        return line_to_write


class Table(TableBase):
    """Read data from the given table file"""

    def _get_data(self):
        #if self._args.verbose:
        #    print("Reading Briggs' motl table file...", file=sys.stderr)

        with open(self.fn, "rb") as motl:
            motl.seek(128 * 4)  # keep an eye
            raw_data = motl.read()
            length = len(raw_data) / 4
            raw_values = struct.unpack("%df" % length, raw_data)

        for i, each in enumerate(raw_values[0:len(raw_values):20]):
            flag = 20 * i
            row = []
            for value in raw_values[flag:(flag + 20)]:
                row.append(value)
            self.col_data.append(row)

        try:
            length_row = [len(row) for row in self.col_data]
            assert sum(length_row) / len(length_row) == length_row[0]
        except AssertionError:
            raise ValueError("Number of columns are not equal on all rows!")

        return len(self.col_data[0]), len(self.col_data), self.col_data

    def __getitem__(self, index):
        return TableRow(self.col_data[index])

    def __iter__(self):
        return iter(map(TableRow, self.col_data))

    def __len__(self):
        return len(self.rows)
