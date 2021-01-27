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


class MotlRow:
    def __init__(self, motl_row, voxel_size=(1.0, 1.0, 1.0)):
        self.row = motl_row
        self.size = voxel_size
        # change each element in the tbl_row into float
        self.dx, self.dy, self.dz, self.tdrot, self.tilt, self.narot, \
        self.x, self.y, self.z = self._get_data()
        self.transformation = self._transform()

    def _get_data(self):
        dx, dy, dz = float(self.row[10]), float(self.row[11]), float(self.row[12])  # todo: fix here
        if dx != 0 or dy != 0 or dz != 0:
            raise ValueError("shifts in x, y, z are note equal to zero")

        tdrot, tilt, narot = float(self.row[17]), float(self.row[18]), float(self.row[16])
        x, y, z = float(self.row[7]), float(self.row[8]), float(self.row[9])
        return dx, dy, dz, tdrot, tilt, narot, x, y, z

    def _transform(self):
        matrix_z_inv = np.linalg.inv(matrix_z(math.radians(self.tdrot)))
        matrix_x_inv = np.linalg.inv(matrix_x(math.radians(self.tilt)))
        matrix_z_inv_2 = np.linalg.inv(matrix_z(math.radians(self.narot)))
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
        return f"Tbl_row={self.row}, voxel_size={self.size}"
