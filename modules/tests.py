import argparse
import base64
import io
import math
import random
import sys
import unittest
import re
import binascii
from unittest.mock import Mock
import os

import combine_modules as cm
import numpy as np
from combine_modules import Map, Tbl, TblRow, EM


# trick: use shlex to parse commands

# we are inheriting the unittest.TestCase class
# it has builtin special assertion methods
# the full list of assertion methods can be found beginning at https://docs.python.org/3/library/unittest.html#assert-methods
# read more about TestCase https://docs.python.org/3/library/unittest.html#assert-methods
# add a docstring so that on verbose test runs (python -m unittest tests -v) you can see what each test is about

# Create a directory that stores the test output files.
# Removed after all the tests were done


class TestRotationMatrices(unittest.TestCase):

    def setUp(self) -> None:
        self.a, self.b, self.c = math.radians(90), math.radians(90), math.radians(90)
        self.dot = np.array([[1], [0], [0]])
        self.dot2 = np.array([[-1], [-1], [0]])

    def tearDown(self) -> None:
        print('test finished!')

    def test_matrix_z(self):
        # anticlockwise rotation
        # fixme: implies opposite convension
        _matrix = cm.matrix_z(self.a)

        test = _matrix.dot(self.dot)
        test2 = _matrix.dot(self.dot2)
        expect = np.array([[0], [-1], [0]])
        expect2 = np.array([[-1], [1], [0]])
        self.assertTrue(np.allclose(test, expect))
        self.assertTrue(np.allclose(test2, expect2))

    def test_matrix_x(self):
        _matrix = cm.matrix_x(self.a)

        test = _matrix.dot(self.dot)
        test2 = _matrix.dot(self.dot2)
        expect = np.array([[1], [0], [0]])
        expect2 = np.array([[-1], [0], [1]])
        self.assertTrue(np.allclose(test, expect))
        self.assertTrue(np.allclose(test2, expect2))

    def test_matrix_y(self):
        _matrix = cm.matrix_y(self.a)

        test = _matrix.dot(self.dot)
        test2 = _matrix.dot(self.dot2)
        expect = np.array([[0], [0], [1]])
        expect2 = np.array([[0], [-1], [-1]])
        self.assertTrue(np.allclose(test, expect))
        self.assertTrue(np.allclose(test2, expect2))

    def test_zxz(self):
        # Useful visualization
        # http://danceswithcode.net/engineeringnotes/rotations_in_3d/demo3D/rotations_in_3d_tool.html

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

    def test_unsupported_convention(self):
        # Try a Tait-Bryan convention
        with self.assertRaises(NameError):
            cm.rotate(self.a, self.b, self.c, convention="xyz")


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

    def test_voxel_size(self):
        self.voxel = self.map.voxel_size
        voxel_size = (self.voxel.x, self.voxel.y, self.voxel.z)
        self.assertEqual((np.float32(5.43), np.float32(5.43), np.float32(5.43)), voxel_size)

    def test_mode(self):
        self.assertEqual(self.map.mode, 2)


class TestTbl(unittest.TestCase):
    def test_row_col_number(self):
        with open("emd_1305_averaged.tbl", "r") as tbl:
            row1 = tbl.readline()
            row2 = tbl.readline()[0:(len(row1) - 2)]
            with open("rm_fake.tbl", "w") as fake:
                fake.write(row1 + row2)
        with self.assertRaises(ValueError):
            Tbl._get_data(self, fn="rm_fake.tbl")  # Because there are unequal number of elements in each row
        os.remove("rm_fake.tbl")

class TestTblRow(unittest.TestCase):
    def setUp(self) -> None:
        self.tblfn = "emd_1305_averaged.tbl"
        self.tbl = Tbl(self.tblfn)
        self.tbl_col = self.tbl.col
        self.map = Map("emd_1305.map")
        self.size = self.map.voxel_size.tolist()
        self.row = TblRow(self.tbl[0], self.size)
        self.tblrow = TblRow(self.tbl[0], self.size)
        self.t = self.tblrow.transformation
        self.em = EM("emd_1305_averaged.em")
        self.box = self.em.volume_array.shape
        self.origin = self.map.origin

        with open(self.tblfn) as tbl:
            first_line = tbl.readline().split(" ")
            self.tdrot, self.tilt, self.narot = float(first_line[6]), float(first_line[7]), float(first_line[8])
            self.ox, self.oy, self.oz = float(first_line[23]), float(first_line[24]), float(first_line[25])
            self.dx, self.dy, self.dz = float(first_line[3]), float(first_line[4]), float(first_line[5])

    def test_box_size(self):
        self.assertAlmostEqual(40, self.box[0])
        self.assertAlmostEqual(40, self.box[1])
        self.assertAlmostEqual(40, self.box[2])

    def test_origin(self):
        self.assertAlmostEqual(-162, self.origin[0])
        self.assertAlmostEqual(-162, self.origin[1])
        self.assertAlmostEqual(-162, self.origin[2])

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

    def test_get_data(self):
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
        # fixme: this is illustrative of a natural opportunity presented by tests to refactor
        # the refactoring suggested is to introduce a function/method that computes translation
        # once we test rotation & translation independently we can test concatenation manually
        random_row = self.get_random_row()
        tbl_row = TblRow(random_row, self.size)
        transform1 = tbl_row._transform()
        vs = 5.43

        test_r = cm.rotate(math.radians(random_row[6]),
                           math.radians(random_row[7]), math.radians(random_row[8]), convention="zxz")

        # Test rotation
        self.assertEqual(test_r.shape, transform1[:, 0:3].shape)
        self.assertTrue(np.allclose(test_r, transform1[:, 0:3]))

        test_dx, test_dy, test_dz = random_row[3], random_row[4], random_row[5]
        test_x, test_y, test_z = random_row[23], random_row[24], random_row[25]
        # since test_algorithm() in class TestOutput succeeded
        test_t = np.array([
            [5.43 * (test_dx * 5.43 + test_x)],
            [5.43 * (test_dy * 5.43 + test_y)],
            [5.43 * (test_dz * 5.43 + test_z)]
        ])

        # combine the test_r and test_t
        transform2 = np.concatenate((test_r, test_t), axis=1)
        print(transform1[-1, -1])
        print(transform2[-1, -1])
        self.assertTrue(np.allclose(transform1, transform2))

    def test_transformation_shape(self):
        self.assertEqual((3, 4), self.t.shape)

    def test_printing(self):
        with open(self.tblfn, "r") as tbl:
            row = TblRow(tbl.readline().rstrip().split(" "), voxel_size=self.size)
        self.assertEqual(
            f"Tbl_row={str(row.row)}, voxel_size={str(self.size)}",
            self.row.__str__()
        )


class TestEM(unittest.TestCase):
    def setUp(self):
        self.em_fn = "emd_1305_averaged.em"
        self.em = EM(self.em_fn)

    def test_dy_mode(self):
        # Tests to ensure only desired modes exist
        self.assertIsInstance(self.em.dy_mode, int)
        self.assertIn(self.em.dy_mode, [2, 4, 5, 9])
        em_fn2 = "tests/emd_1305_mode2.em"
        em_fn4 = "tests/emd_1305_mode4.em"
        em_fn9 = "tests/emd_1305_mode9.em"
        em2 = EM(em_fn2)
        em4 = EM(em_fn4)
        em9 = EM(em_fn9)
        self.assertEqual(int(em2.dy_mode), 2)
        self.assertEqual(int(em4.dy_mode), 4)
        self.assertEqual(int(em9.dy_mode), 9)

        with self.assertRaises(NotImplementedError):
            em_fn8 = "tests/emd_1305_mode8.em"
            em8 = EM(em_fn8)
            print(em8.dy_mode)

    def test_box(self):
        self.assertEqual(40, self.em.nc)
        self.assertEqual(40, self.em.nr)
        self.assertEqual(40, self.em.ns)

    def test_volume_encoded(self):
        # check whether is it encoded in base64
        # a regular expression of base64 string: ^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$
        self.assertTrue(
            re.match(rb"^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$", self.em.volume_encoded))

    def test_zlib_compressed(self):
        data = self.em.volume_encoded_compressed
        data_binary = base64.b64decode(data)[:4]
        ascii_hex = binascii.b2a_hex(data_binary)
        """
        Recognizing zlib compression:
        https://isc.sans.edu/forums/diary/Recognizing+ZLIB+Compression/25182/
        The zlib generated data is structured according to RFC 1950. 
        The first byte (0x78) is the compression method and flags
        - 7801: No compression/low compression
        - 789C: zlib default compression
        - 78DA: zlib best compression
        """
        zlib_flag = [bytes("7801", "utf-8"), bytes("789c", "utf-8"), bytes("78da", "utf-8")]
        flag = 0
        if ascii_hex[0:4] in zlib_flag:
            flag = 1
        self.assertEqual(flag, 1)

    def test_volume_array(self):
        self.assertEqual(self.em.volume_array.shape, (40, 40, 40))


class TestRearrangeMatrix(unittest.TestCase):
    def setUp(self):
        mock_args = Mock(data="emd_1305_averaged", map_file="emd_1305.map")
        self.tbl_test, self.transformations_test = cm.rearrange_matrix(mock_args)

    def test_tbl(self):
        actual_tbl = cm.Tbl("emd_1305_averaged.tbl")
        self.assertEqual(actual_tbl[0], self.tbl_test[0])

    def test_transformations(self):
        map_fn = "emd_1305.map"
        map = Map(map_fn)  # wanted
        size = map.voxel_size.tolist()
        em_fn = "emd_1305_averaged.em"
        em = EM(em_fn)  # wanted
        box = em.volume_array.shape
        tbl_fn = "emd_1305_averaged.tbl"
        tbl = Tbl(tbl_fn)
        tbl_row = TblRow(tbl[0], size)  # wanted

        transformation_m = tbl_row.transformation
        origin = map.origin

        ox = origin[0].tolist()
        oy = origin[1].tolist()
        oz = origin[2].tolist()

        o_m = np.array(
            [[0, 0, 0, ox * size[0]], [0, 0, 0, oy * size[1]], [0, 0, 0, oz * size[2]]])
        halfbox_m = np.array([[0, 0, 0, box[0] * size[0] / 2], [0, 0, 0, box[1] * size[1] / 2],
                              [0, 0, 0, box[2] * size[2] / 2]])

        self.assertTrue(np.allclose(self.transformations_test[0], transformation_m + o_m - halfbox_m))


class TestOutput(unittest.TestCase):
    def test_output_name_uncompressed(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        mock_args = Mock(data="emd_1305_averaged", map_file="emd_1305.map", compress=False, output=False,
                         map_start=False)
        cm.create_output(mock_args)
        self.assertTrue(os.path.exists("emd_1305_averaged_nc.txt"))
        self.assertTrue("not compressed" in captured_output.getvalue())
        os.remove("emd_1305_averaged_nc.txt")

    def test_output_name_compressed(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        mock_args = Mock(data="emd_1305_averaged", map_file="emd_1305.map", compress=True, output=False,
                         map_start=False)
        cm.create_output(mock_args)
        self.assertTrue(os.path.exists("emd_1305_averaged_c.txt"))
        self.assertTrue("is compressed" in captured_output.getvalue())
        os.remove("emd_1305_averaged_c.txt")

    def test_output_name_specified_nc(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        mock_args = Mock(data="emd_1305_averaged", map_file="emd_1305.map", compress=False, output="rm_nc",
                         map_start=False)
        cm.create_output(mock_args)
        self.assertTrue(os.path.exists("rm_nc.txt"))
        self.assertTrue("not compressed" in captured_output.getvalue())
        os.remove("rm_nc.txt")

    def test_output_name_specified_c(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        mock_args = Mock(data="emd_1305_averaged", map_file="emd_1305.map", compress=True, output="rm_c",
                         map_start=False)
        cm.create_output(mock_args)
        self.assertTrue(os.path.exists("rm_c.txt"))
        self.assertTrue("is compressed" in captured_output.getvalue())
        os.remove("rm_c.txt")

    def test_print_map_start(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output

        mock_args = Mock(data="emd_1305_averaged", map_file="emd_1305.map", compress=False, output="rm_nc_2",
                         map_start=True, voxel_size=False)
        cm.create_output(mock_args)
        self.assertTrue("nxstart: -162\nnystart: -162\nnzstart: -162" in captured_output.getvalue())
        os.remove("rm_nc_2.txt")

    def test_print_voxel_size(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output

        mock_args = Mock(data="emd_1305_averaged", map_file="emd_1305.map", compress=False, output="rm_3",
                         voxel_size=True)
        cm.create_output(mock_args)
        self.assertTrue("voxel_size in x, y, z: (5.43, 5.43, 5.43)" in captured_output.getvalue())
        os.remove("rm_3.txt")


class Test_Parser(unittest.TestCase):
    def test_data_name_has_em_tbl_and_map(self):
        """test that the file with {args.data}.em, {args.data}.tbl and {args.map_file} exist"""
        sys.argv = ["something", "--data", "emd_1305_averaged", "--map-file", "emd_1305.map"]
        args = cm.parse_args()

        self.assertTrue(os.path.exists(f"{args.data}.em"))
        self.assertTrue(os.path.exists(f"{args.data}.tbl"))
        self.assertTrue(os.path.exists(f"{args.map_file}"))
        self.assertEqual(args.compress, 0)
        self.assertEqual(args.map_start, 0)
        self.assertEqual(args.voxel_size, 0)

    def test_data_is_comrpessed(self):
        """Test when '-c' or '--compress' given, its 'action' is true*. """
        sys.argv = ["something", "--data", "emd_1305_averaged", "--map-file", "emd_1305.map", "--compress"]
        args = cm.parse_args()
        self.assertEqual(args.compress, 1)

    def test_pirnt_origin(self):
        """Test when '-s' given, print the origin of the .em data"""
        sys.argv = ["something", "--data", "emd_1305_averaged", "--map-file", "emd_1305.map", "-s"]
        args = cm.parse_args()
        self.assertEqual(args.map_start, 1)

    def test_print_voxel_size(self):
        """Test when 'v' given, print the voxel_size of the .em data"""
        sys.argv = ["something", "--data", "emd_1305_averaged", "--map-file", "emd_1305.map", "-v"]
        args = cm.parse_args()
        self.assertEqual(args.voxel_size, 1)


class Test_Main(unittest.TestCase):
    def test_emdata_not_in_path(self):
        """Test whether the system raises ValueError if the given .em or .tbl file does not exist in the path"""
        sys.argv = ["something", "--data", "tests/test_main_em_error", "--map-file", "emd_1305.map"]
        with self.assertRaises(ValueError):
            cm.main()

    def test_tbl_not_in_path(self):
        """Test whether the system raises ValueError if the given .tbl file does not exist in the path"""
        sys.argv = ["something", "--data", "tests/test_main_tbl_error", "--map-file", "emd_1305_averaged.map"]
        with self.assertRaises(ValueError):
            cm.main()

    def test_map_not_in_path(self):
        sys.argv = ["something", "--data", "emd_1305_averaged", "--map-file", "emd_1305_averaged.map"]
        with self.assertRaises(ValueError):
            cm.main()

    def test_calls_create_output_function(self):
        """Test if main() is executed, create_output() is run"""
        sys.argv = ["something", "--data", "emd_1305_averaged", "--map-file", "emd_1305.map", "--output", "rm_4"]
        cm.main()
        self.assertTrue(os.path.exists("rm_4.txt"))
        os.remove("rm_4.txt")

class Test_exit(unittest.TestCase):
    def test_system_exit(self):
        sys.argv = sys.argv = ["something", "--data", "emd_1305_averaged", "--map-file", "emd_1305.map", "--output", "rm_5"]
        cm.main()
        print(os.system(cm))
        self.assertTrue(False)
        # os.remove("rm_5.txt")
