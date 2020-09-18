import unittest
import voxel_dynamo as voxel

# we are inheriting the unittest.TestCase clas
# it has builtin special assertion methods
# the full list of assertion methods can be found beginning at https://docs.python.org/3/library/unittest.html#assert-methods
# read more about TestCase https://docs.python.org/3/library/unittest.html#assert-methods
# add a docstring so that on verbose test runs (python -m unittest tests -v) you can see what each test is about
class EMDBassist(unittest.TestCase):
    def setUp(self) -> None:
        # initialise before each test is run
        self.filename = 'a.em'
        self.em = voxel.EM(self.filename)

    def tearDown(self) -> None:
        print('test finished!')

    def test_filename(self):
        """Tests to ensure the filename attribute exists and is correct"""
        self.assertEqual(self.em.filename, 'a.em')

    def test_dy_mode(self):
        self.assertIsInstance(self.em.dy_mode, int)
        self.assertIn(self.em.dy_mode, [2, 4, 5, 9])


if __name__ == "__main__":
    unittest.main()
