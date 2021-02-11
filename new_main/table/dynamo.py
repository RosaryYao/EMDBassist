# Define rotation matrices (anticlockwise)
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
        raise NameError("convention not supported!")


class TblRow:
    def __init__(self, tbl_row, voxel_size=(1.0, 1.0, 1.0)):
        self.row = tbl_row
        self.size = voxel_size
        # change each element in the tbl_row into float
        self.dx, self.dy, self.dz, self.tdrot, self.tilt, self.narot, \
        self.x, self.y, self.z, self.dshift, self.daxis, self.dnarot = self._get_data()
        self.transformation = self._transform()

    def _get_data(self):
        dx, dy, dz = float(self.row[3]), float(self.row[4]), float(self.row[5])
        tdrot, tilt, narot = float(self.row[6]), float(self.row[7]), float(self.row[8])
        x, y, z = float(self.row[23]), float(self.row[24]), float(self.row[25])
        dshift, daxis, dnarot = float(self.row[26]), float(self.row[27]), float(self.row[28])
        return dx, dy, dz, tdrot, tilt, narot, x, y, z, dshift, daxis, dnarot

    # todo: Caution! Additional *self.size[i]. WHY???
    def _transform(self):
        rotation = rotate(math.radians(self.tdrot), math.radians(self.tilt), math.radians(self.narot))
        transformation = np.insert(rotation, 3, [(self.x + self.dx * self.size[0]) * self.size[0],
                                                 (self.y + self.dy * self.size[0]) * self.size[1],
                                                 (self.z + self.dz * self.size[0]) * self.size[2]], axis=1)

        return transformation

    def __str__(self):
        return f"Tbl_row={self.row}, voxel_size={self.size}"



