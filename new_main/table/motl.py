import numpy as np
import math


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


class Table:
    def __init__(self, motl_row, voxel_size=(1.0, 1.0, 1.0)):
        self.row = motl_row
        # change each element in the tbl_row into float
        self.dx, self.dy, self.dz, self.tdrot, self.tilt, self.narot, \
        self.x, self.y, self.z = self._get_data()
        self.transformation = self._transform()

    def _get_data(self):
        dx, dy, dz = float(self.row[10]), float(self.row[11]), float(self.row[12])  # todo: fix here
        #if dx != 0 or dy != 0 or dz != 0:
        #    raise ValueError("shifts in x, y, z are note equal to zero")

        tdrot, tilt, narot = math.radians(float(self.row[17])), math.radians(float(self.row[18])), math.radians(float(self.row[16]))
        x, y, z = float(self.row[7]+dx), float(self.row[8]+dy), float(self.row[9]+dz)
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

        transformation = np.insert(rotation, 3, translation, axis=1)
        return transformation

    def __str__(self):
        return f"Tbl_row={self.row}"
