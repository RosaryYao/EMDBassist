import unittest
import voxel_dynamo as voxel
import transformation_dynamo as transform
import combine_modules as combine
import random
import math
import numpy as np

# we are inheriting the unittest.TestCase class
# it has builtin special assertion methods
# the full list of assertion methods can be found beginning at https://docs.python.org/3/library/unittest.html#assert-methods
# read more about TestCase https://docs.python.org/3/library/unittest.html#assert-methods
# add a docstring so that on verbose test runs (python -m unittest tests -v) you can see what each test is about
class EMDBassist(unittest.TestCase):
    def setUp(self) -> None:
        # initialise before each test is run
        self.filename = 'a.em'
        self.tbl = 'a.tbl'
        self.em = voxel.EM(self.filename)


    def tearDown(self) -> None:
        print('test finished!')

    def test_filename(self):
        """Tests to ensure the filename attribute exists and is correct"""
        self.assertEqual(self.em.filename, 'a.em')

    def test_dy_mode(self):
        """Tests to ensure only desired modes exist"""
        self.assertIsInstance(self.em.dy_mode, int)
        self.assertIn(self.em.dy_mode, [2, 4, 5, 9])

    def test_rotation_matrix(self):
        """
        Tests to ensure rotation matrices are correct.
        Useful visualization: http://danceswithcode.net/engineeringnotes/rotations_in_3d/demo3D/rotations_in_3d_tool.html
        """

        a, b, c = math.radians(90), math.radians(90), math.radians(90)
        self.rotate_zxz = transform.Polygon().rotate(a=a, b=b, c=c)

        dot = np.array([[1], [0], [0]])
        final_dot = np.array([[0], [0], [1]])

        dot2 = np.array([[-1], [-1], [0]])
        final_dot2 = np.array([[], [], []])

        # Test rotation matrix
        self.assertEqual(final_dot.tolist(), self.rotate_zxz.dot(dot).tolist())









if __name__ == "__main__":
    unittest.main()
