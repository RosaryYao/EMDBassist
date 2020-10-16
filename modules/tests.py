import argparse
import math
import random
import unittest

import combine_modules as cm
import numpy as np
from combine_modules import Map, Tbl, TblRow, EM

# trick: use shlex to parse commands

# we are inheriting the unittest.TestCase class
# it has builtin special assertion methods
# the full list of assertion methods can be found beginning at https://docs.python.org/3/library/unittest.html#assert-methods
# read more about TestCase https://docs.python.org/3/library/unittest.html#assert-methods
# add a docstring so that on verbose test runs (python -m unittest tests -v) you can see what each test is about

""" 
class EMDBassist(unittest.TestCase):

    def setUp(self) -> None:
        self.a, self.b, self.c = math.radians(90), math.radians(90), math.radians(90)
        self.dot = np.array([[1], [0], [0]])
        self.dot2 = np.array([[-1], [-1], [0]])

    def tearDown(self) -> None:
        print('test finished!')

    def test_dy_mode(self):
        ### Tests to ensure only desired modes exist
        self.assertIsInstance(self.em.dy_mode, int)
        self.assertIn(self.em.dy_mode, [2, 4, 5, 9])

    def test_matrix_z(self):
        # unit vector along +x (1, 0, 0)
        v = np.array([[1], [0], [0]])
        # apply rotation around z: 90
        _matrix = cm.matrix_z(math.radians(90))
        print(f"matrix: {_matrix}")
        vp = _matrix.dot(v)
        # expect: (0, 1, 0)
        self.assertTrue(np.allclose(vp, np.array([[0], [1], [0]])))

    def test_matrix_x(self):
        # unit vector along +y (0, 1, 0)
        v = np.array([[0], [1], [0]])
        # apply rotation around x: 90
        vp = cm.matrix_x(math.radians(90)).dot(v)
        # expect: (0, 0, 1)
        self.assertTrue(np.allclose(vp, np.array([[0], [0], [1]])))

    def test_matrix_y(self):
        # unit vector along +y (0, 0, 1)
        v = np.array([[0], [0], [1]])
        # apply rotation around y: 90
        vp = cm.matrix_y(math.radians(90)).dot(v)
        # expect: (1, 0, 0)
        self.assertTrue(np.allclose(vp, np.array([[1], [0], [0]])))

    def test_zxz(self):

        ### Tests to ensure rotation matrices are correct.
        ### Useful visualization: http://danceswithcode.net/engineeringnotes/rotations_in_3d/demo3D/rotations_in_3d_tool.html
        
        rotate_zxz = cm.rotate(self.a, self.b, self.c, convention="zxz")

        final_dot = np.array([[0], [0], [1]])
        final_dot2 = np.array([[0], [1], [-1]])

        # Using other angles are quite difficult to manually calculate the correct coordinates
        self.assertTrue(np.allclose(rotate_zxz.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_zxz.dot(self.dot2), final_dot2))

    def test_zyz(self):
        ###Check that zyz is calculated correctly

        rotate_zyz = cm.rotate(self.a, self.b, self.c, convention="zyz")

        final_dot = np.array([[-1], [0], [0]])
        final_dot2 = np.array([[1], [0], [-1]])

        self.assertTrue(np.allclose(rotate_zyz.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_zyz.dot(self.dot2), final_dot2))

    def test_yzy(self):
        rotate_yzy = cm.rotate(self.a, self.b, self.c, convention="yzy")

        final_dot = np.array([[-1], [0], [0]])
        final_dot2 = np.array([[1], [0], [-1]])

        self.assertTrue(np.allclose(rotate_yzy.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_yzy.dot(self.dot2), final_dot2))

    def test_yxy(self):

        rotate_yxy = cm.rotate(self.a, self.b, self.c, convention="yxy")

        final_dot = np.array([[0], [1], [0]])
        final_dot2 = np.array([[-1], [-1], [0]])

        self.assertTrue(np.allclose(rotate_yxy.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_yxy.dot(self.dot2), final_dot2))

    def test_xzx(self):
        rotate_xzx = cm.rotate(self.a, self.b, self.c, convention="xzx")

        final_dot = np.array([[0], [0], [1]])
        final_dot2 = np.array([[0], [1], [-1]])

        self.assertTrue(np.allclose(rotate_xzx.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_xzx.dot(self.dot2), final_dot2))

    def test_xyx(self):
        rotate_xyx = cm.rotate(self.a, self.b, self.c, convention="xyx")

        final_dot = np.array([[0], [1], [0]])
        final_dot2 = np.array([[-1], [-1], [0]])

        self.assertTrue(np.allclose(rotate_xyx.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_xyx.dot(self.dot2), final_dot2))

    def test_transformation(self):
        # todo: check that the matrix in the output txt has shape 3*4, and corresponds to the correct order?
        # todo: to check the translation is correct - have map start coordinates added
        # tbl_transformation + map_start = real_transformation/output_transformation

        real_transformation = []
        output_transformation = []

        with open(self.tbl, "r") as tbl:
            x = float(self.map_header.nxstart)
            y = float(self.map_header.nystart)
            z = float(self.map_header.nzstart)
            for line in tbl:
                line = str(line).split(" ")
                real_transformation.append(
                    [str(float(line[23]) + x), str(float(line[24]) + y), str(float(line[25]) + z)])

        with open(self.output, "r") as output:
            for line in output:
                if line[0] in map(str, range(10)):
                    data = line.strip('\n').split('\t')[1:]
                    output_transformation.append([data[3], data[7], data[11]])

        self.assertEqual(len(data), 12)
        self.assertEqual(len(real_transformation), 20)
        self.assertEqual(len(output_transformation), 20)
        self.assertEqual(real_transformation, output_transformation)
"""


class TestMap(unittest.TestCase):
    def setUp(self) -> None:
        self.fn = "emd_1305.map"
        self.map = cm.Map(self.fn)
        self.origin = self.map.origin

    def tearDown(self) -> None:
        print('test finished!')

    def test_origin(self):
        actual_origin = (-162, -162, -162)
        self.assertEqual(actual_origin, self.origin)

    def test_matrix(self):
        origin_matrix = np.array([
            [0, 0, 0, self.origin[0]], [0, 0, 0, self.origin[1]], [0, 0, 0, self.origin[2]]
        ])
        actual_o_matrix = np.array([
            [0, 0, 0, -162], [0, 0, 0, -162], [0, 0, 0, -162]
        ])
        self.assertTrue(np.allclose(origin_matrix, actual_o_matrix))

    def test_voxel_size(self):
        self.voxel = self.map.voxel_size
        voxel_size = (self.voxel.x, self.voxel.y, self.voxel.z)
        self.assertEqual((np.float32(5.43), np.float32(5.43), np.float32(5.43)), voxel_size)

    def test_mode(self):
        self.assertEqual(self.map.mode, 2)


class TestTblRow(unittest.TestCase):
    def setUp(self) -> None:
        self.tblfn = "emd_1305_averaged.tbl"
        self.tbl = Tbl(self.tblfn)
        self.tbl_col = self.tbl.col
        self.map = Map("emd_1305.map")
        self.size = self.map.voxel_size.tolist()
        # self.voxel_size = self.map.voxel_size
        self.tblrow = TblRow(self.tbl[0], self.size)
        self.t = self.tblrow.transformation
        self.em = EM("emd_1305_averaged.em")
        self.box = self.em.volume_array.shape
        self.origin = self.map.origin

        #
        with open(self.tblfn) as tbl:
            first_line = tbl.readline().split(" ")
            self.tdrot, self.tilt, self.narot = float(first_line[6]), float(first_line[7]), float(first_line[8])
            self.ox, self.oy, self.oz = float(first_line[23]), float(first_line[24]), float(first_line[25])
            self.dx, self.dy, self.dz = float(first_line[3]), float(first_line[4]), float(first_line[5])

    def get_random_row(self):
        # Generate data with the same number of columns
        random_row = [
            random.randint(0, 100),  # tag
            random.randint(0, 1),
            random.randint(0, 1),
            random.randint(-5, 5),
            random.randint(-5, 5),
            random.randint(-5, 5),
            random.random() * random.choice([-360, 360]),
            random.random() * random.choice([-360, 360]),
            random.random() * random.choice([-360, 360]),
            random.randint(0, 1),
            random.randint(0, 1),
            random.randint(0, 1),
            random.randint(0, 1),
            # mintilt 14-17
            random.random() * random.choice([-360, 360]),
            random.random() * random.choice([-360, 360]),
            random.random() * random.choice([-360, 360]),
            random.random() * random.choice([-360, 360]),
            # 18-23
            random.randint(0, 10),
            random.randint(0, 10),
            random.randint(0, 100),
            random.randint(0, 10),
            random.randint(0, 10),
            random.randint(0, 10),
            # 24-26 x,y,z coordinates
            random.random() * random.randint(-1000, 1000),
            random.random() * random.randint(-1000, 1000),
            random.random() * random.randint(-1000, 1000),
            # d(angle) 27-29
            random.random() * random.randint(-360, 360),
            random.random() * random.randint(-360, 360),
            random.random() * random.randint(-360, 360),
            # 30, 31, 32, 34, 35
            random.random() * random.choice([-1, 1]),
            random.randint(0, 1),
            random.randint(0, 1),
            random.randint(0, 1),
            random.randint(0, 1),
            random.randint(0, 1),
        ]

        return random_row

    def test_columns(self):
        random_row = self.get_random_row()
        self.assertEqual(len(random_row), self.tbl_col)

        # if i instantiate a TblRow object are the attributes correct
        row_data = self.get_random_row()
        tblrow = TblRow(row_data)
        self.assertEqual(tblrow.dx, row_data[3])
        self.assertEqual(tblrow.dy, row_data[4])
        self.assertEqual(tblrow.dz, row_data[5])
        self.assertEqual(tblrow.tdrot, row_data[6])
        self.assertEqual(tblrow.tilt, row_data[7])
        self.assertEqual(tblrow.narot, row_data[8])
        self.assertEqual(tblrow.x, row_data[23])
        self.assertEqual(tblrow.y, row_data[24])
        self.assertEqual(tblrow.z, row_data[25])
        self.assertEqual(tblrow.dshift, row_data[26])
        self.assertEqual(tblrow.daxis, row_data[27])
        self.assertEqual(tblrow.dnarot, row_data[28])

    def test_transform(self):
        random_row = self.get_random_row()
        tbl_row = TblRow(random_row,)
        transform1 = tbl_row._transform()
        print(f"transform:\n{transform1}")
        vs = 5.43
        tbl_row = TblRow(random_row, voxel_size=(vs, vs, vs))
        transform2 = tbl_row._transform()
        print(f"transform:\n{transform2}")
        self.assertEqual(transform2.shape, (3, 4))
        print(f"last column: {transform2[:,3]}")
        a = transform1[:, 3] * vs
        b = transform2[:, 3]
        print(f"a\n{a}")
        print(f"b\n{b}")
        self.assertEqual(np.allclose(a, b))

    def test_transformation_shape(self):
        self.assertEqual((3, 4), self.t.shape)

    def test_rotation(self):
        self.rotation = np.delete(self.t, np.s_[-1], 1)

        true_rotation = cm.rotate(math.radians(self.tdrot), math.radians(self.tilt), math.radians(self.narot))
        print(self.rotation)
        self.assertTrue(np.allclose(self.rotation, true_rotation))

    def test_translation(self):
        translation_column = np.delete(self.t, np.s_[:-1], 1).T
        print(self.t)

        # The "wanted true translation matrix"
        self.tbl_translation = [(self.ox + self.dx) * self.voxel[0], (self.oy + self.dy) * self.voxel[1],
                                (self.oz + self.dz) * self.voxel[2]]
        self.assertEqual(self.translation[0], self.tbl_translation[0])
        print(self.translation)


class TestOutput(unittest.TestCase):
    def setUp(self):
        # "a" stands for "actual", which is the desired output
        self.a_fn = "actual_1305_output.txt"
        with open(self.a_fn) as f:
            self.a_row = f.readline().split(",")[1:]

        # Initialize the information
        self.map_fn = "emd_1305.map"
        self.map = Map(self.map_fn)  # wanted
        self.size = self.map.voxel_size.tolist()
        self.em_fn = "emd_1305_averaged.em"
        self.em = EM(self.em_fn)  # wanted
        self.box = self.em.volume_array.shape
        self.tbl_fn = "emd_1305_averaged.tbl"
        self.tbl = Tbl(self.tbl_fn)
        self.tbl_row = TblRow(self.tbl[0], self.size)  # wanted

        self.transformation_m = self.tbl_row.transformation
        self.origin = self.map.origin

        self.box = self.em.volume_array.shape

        # Look inside the output file
        self.output_fn = ""

    def test_algorithm(self):
        self.ox = self.origin[0].tolist()
        self.oy = self.origin[1].tolist()
        self.oz = self.origin[2].tolist()

        o_m = np.array(
            [[0, 0, 0, self.ox * self.size[0]], [0, 0, 0, self.oy * self.size[1]], [0, 0, 0, self.oz * self.size[2]]])
        halfbox_m = np.array([[0, 0, 0, self.box[0] * self.size[0] / 2], [0, 0, 0, self.box[1] * self.size[1] / 2],
                              [0, 0, 0, self.box[2] * self.size[2] / 2]])

        self.assertTrue(np.allclose(o_m[0][3], -162 * 5.43))
        self.assertTrue(np.allclose(halfbox_m[0][3], 20 * 5.43))
        print(self.transformation_m[0][3])
        self.assertTrue(np.allclose(self.transformation_m + o_m - halfbox_m)[0][3], self.a_row[3])


if __name__ == "__main__":
    # Argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--em", metavar="", required=True, help="the Dynamo .em file.")
    parser.add_argument("-t", "--tbl", metavar="", required=True, help="the Dynamo .tbl file")
    args = parser.parse_args()
    unittest.main(args)
