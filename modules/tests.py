import math
import unittest
import numpy as np
import argparse
import sys

import voxel_dynamo as voxel
from combine_modules import rotate


# we are inheriting the unittest.TestCase class
# it has builtin special assertion methods
# the full list of assertion methods can be found beginning at https://docs.python.org/3/library/unittest.html#assert-methods
# read more about TestCase https://docs.python.org/3/library/unittest.html#assert-methods
# add a docstring so that on verbose test runs (python -m unittest tests -v) you can see what each test is about



class EMDBassist(unittest.TestCase):
    def setUp(self) -> None:
        # initialise before each test is run
        self.filename = args.em
        self.tbl = args.tbl

        self.em = voxel.EM(self.filename)
        self.a, self.b, self.c = math.radians(90), math.radians(90), math.radians(90)
        self.dot = np.array([[1], [0], [0]])
        self.dot2 = np.array([[-1], [-1], [0]])

    def tearDown(self) -> None:
        print('test finished!')

    # todo: consider removing this test?
    def test_filename(self):
        """Tests to ensure the filename attribute exists and is correct"""
        self.assertEqual(self.em.filename, 'a.em')

    def test_dy_mode(self):
        """Tests to ensure only desired modes exist"""
        self.assertIsInstance(self.em.dy_mode, int)
        self.assertIn(self.em.dy_mode, [2, 4, 5, 9])

    def test_zxz(self):
        """
        Tests to ensure rotation matrices are correct.
        Useful visualization: http://danceswithcode.net/engineeringnotes/rotations_in_3d/demo3D/rotations_in_3d_tool.html
        """
        rotate_zxz = rotate(self.a, self.b, self.c, convention="zxz")

        final_dot = np.array([[0], [0], [1]])
        final_dot2 = np.array([[0], [1], [-1]])

        # Using other angles are quite difficult to manually calculate the correct coordinates
        self.assertTrue(np.allclose(rotate_zxz.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_zxz.dot(self.dot2), final_dot2))

    def test_zyz(self):
        """Check that zyz is calculated correctly"""

        rotate_zyz = rotate(self.a, self.b, self.c, convention="zyz")

        final_dot = np.array([[-1], [0], [0]])
        final_dot2 = np.array([[1], [0], [-1]])

        self.assertTrue(np.allclose(rotate_zyz.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_zyz.dot(self.dot2), final_dot2))

    def test_yzy(self):
        rotate_yzy = rotate(self.a, self.b, self.c, convention="yzy")

        final_dot = np.array([[-1], [0], [0]])
        final_dot2 = np.array([[1], [0], [-1]])

        self.assertTrue(np.allclose(rotate_yzy.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_yzy.dot(self.dot2), final_dot2))

    def test_yxy(self):
        rotate_yxy = rotate(self.a, self.b, self.c, convention="yxy")

        final_dot = np.array([[0], [1], [0]])
        final_dot2 = np.array([[-1], [-1], [0]])

        self.assertTrue(np.allclose(rotate_yxy.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_yxy.dot(self.dot2), final_dot2))

    def test_xzx(self):
        rotate_xzx = rotate(self.a, self.b, self.c, convention="xzx")

        final_dot = np.array([[0], [0], [1]])
        final_dot2 = np.array([[0], [1], [-1]])

        self.assertTrue(np.allclose(rotate_xzx.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_xzx.dot(self.dot2), final_dot2))

    def test_xyx(self):
        rotate_xyx = rotate(self.a, self.b, self.c, convention="xyx")

        final_dot = np.array([[0], [1], [0]])
        final_dot2 = np.array([[-1], [-1], [0]])

        self.assertTrue(np.allclose(rotate_xyx.dot(self.dot), final_dot))
        self.assertTrue(np.allclose(rotate_xyx.dot(self.dot2), final_dot2))

    def test_transformation(self):
        # todo: check that the matrix in the output txt has shape 3*4, and corresponds to the correct order?
        self.assertTrue(True)


if __name__ == "__main__":
    # Argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--em", metavar="", required=True, help="the Dynamo .em file.")
    parser.add_argument("-t", "--tbl", metavar="", required=True, help="the Dynamo .tbl file")
    args = parser.parse_args()
    unittest.main(args)
    # todo: error here - unknown arguments -e -t.
