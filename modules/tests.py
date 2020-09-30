import math
import unittest
import numpy as np
import argparse
import sys
# trick: use shlex to parse commands
import shlex
import mrcfile

import voxel_dynamo as voxel
import combine_modules as cm


# we are inheriting the unittest.TestCase class
# it has builtin special assertion methods
# the full list of assertion methods can be found beginning at https://docs.python.org/3/library/unittest.html#assert-methods
# read more about TestCase https://docs.python.org/3/library/unittest.html#assert-methods
# add a docstring so that on verbose test runs (python -m unittest tests -v) you can see what each test is about



class EMDBassist(unittest.TestCase):

    def setUp(self) -> None:
        self.filename = "emd_1305_averaged.em"
        self.tbl = "emd_1305_averaged.tbl"
        self.em = voxel.EM(self.filename)
        self.a, self.b, self.c = math.radians(90), math.radians(90), math.radians(90)
        self.dot = np.array([[1], [0], [0]])
        self.dot2 = np.array([[-1], [-1], [0]])
        self.output = "rm_1305.txt"
        with mrcfile.open("emd_1305.map") as mrc:
            self.map_header = mrc.header

    def tearDown(self) -> None:
        print('test finished!')

    # todo: consider removing this test?
    def test_filename(self):
        """Tests to ensure the filename attribute exists and is correct"""
        self.assertEqual(self.em.filename, 'emd_1305_averaged.em')

    def test_dy_mode(self):
        """Tests to ensure only desired modes exist"""
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
        """
        Tests to ensure rotation matrices are correct.
        Useful visualization: http://danceswithcode.net/engineeringnotes/rotations_in_3d/demo3D/rotations_in_3d_tool.html
        """
        rotate_zxz = cm.rotate(self.a, self.b, self.c, convention="zxz")

        final_dot = np.array([[0], [0], [1]])
        final_dot2 = np.array([[0], [1], [-1]])

        # Using other angles are quite difficult to manually calculate the correct coordinates
        self.assertTrue(np.allclose(rotate_zxz.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_zxz.dot(self.dot2), final_dot2))

    def test_zyz(self):
        """Check that zyz is calculated correctly"""

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
                real_transformation.append([str(float(line[23])+x), str(float(line[24])+y), str(float(line[25])+z)])


        with open(self.output, "r") as output:
            for line in output:
                if line[0] in map(str, range(10)):
                    data = line.strip('\n').split('\t')[1:]
                    output_transformation.append([data[3], data[7], data[11]])

        self.assertEqual(len(data), 12)
        self.assertEqual(len(real_transformation), 20)
        self.assertEqual(len(output_transformation), 20)
        self.assertEqual(real_transformation, output_transformation)





if __name__ == "__main__":
    # Argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--em", metavar="", required=True, help="the Dynamo .em file.")
    parser.add_argument("-t", "--tbl", metavar="", required=True, help="the Dynamo .tbl file")
    args = parser.parse_args()
    unittest.main(args)

