import base64
import binascii
import io
import math
import os
import platform
import random
import sys
import unittest
from unittest import mock

import numpy as np

from .. import TEST_DATA, core_modules
from ..average import motl as motl_a
from ..average import dynamo as dynamo_a
from ..average import peet as peet_a
from ..table import motl as motl_t
from ..table import dynamo as dynamo_t
from ..table import peet as peet_t
from ..parser import parse_args
from .. import utils

cmd = "tra"


class TestCLI(unittest.TestCase):
    def setUp(self) -> None:
        self.file_root = f"{os.path.join(TEST_DATA, 'motl')}/sample"
        if platform.system() == "Windows":
            self.file_root = os.path.normcase(self.file_root)

    def test_default(self):
        sys.argv = f"{cmd} {self.file_root}".split(" ")
        print(sys.argv)
        args = parse_args()
        print(f"The args.file is: {args.file}")
        print(os.path.exists(f"{args.file}.em"))
        print(os.path.exists(f"{self.file_root}.em"))
        self.assertEqual(args.file, self.file_root)
        self.assertEqual(args.table, f"{self.file_root}.em")
        self.assertEqual(args.average, f"{self.file_root}.map")

    def test_explicit(self):
        """User explicitly specifies files"""
        sys.argv = f"{cmd} -T {self.file_root}.em -A {self.file_root}.map".split(" ")
        print(sys.argv)
        args = parse_args()
        self.assertEqual(args.table, f"{self.file_root}.em")
        self.assertEqual(args.average, f"{self.file_root}.map")

        # ensure AssertionError raised when only one specified file given
        sys.argv = f"cmd -T {self.file_root}.em".split(" ")
        # with self.assertRaises(AssertionError):
        #    parse_args()
        # self.assertEqual(parse_args(), os._exit(1))  # todo: fix this...
        os._exit = mock.MagicMock()
        parse_args()
        assert os._exit.called

    def test_dynamo(self):
        self.file_root = f"{os.path.join(TEST_DATA, 'dynamo')}/sample"
        if platform.system() == "Windows":
            self.file_root = os.path.normcase(self.file_root)

        self.assertTrue(os.path.exists(f"{self.file_root}.tbl"))
        self.assertTrue(os.path.exists(f"{self.file_root}.em"))
        sys.argv = f"{cmd} {self.file_root}".split(" ")
        args = parse_args()
        self.assertEqual(args.table, f'{self.file_root}.tbl')
        self.assertEqual(args.average, f'{self.file_root}.em')

    def test_peet(self):
        self.file_root = f"{os.path.join(TEST_DATA, 'peet')}/sample"
        if platform.system() == "Windows":
            self.file_root = os.path.normcase(self.file_root)

        self.assertTrue(os.path.exists(f"{self.file_root}.rec"))
        self.assertTrue(os.path.exists(f"{self.file_root}.mod"))
        sys.argv = f"{cmd} {self.file_root}".split(" ")
        args = parse_args()
        self.assertEqual(args.table, f'{self.file_root}.mod')
        self.assertEqual(args.average, f'{self.file_root}.rec')

    def test_output(self):
        """Ensure that output is handled correctly"""
        file_root = f"{os.path.join(TEST_DATA, 'motl')}/sample"  # windows' format
        print(file_root)
        if platform.system() == "Windows":
            file_root = os.path.normcase(file_root)
        print(f"value of file_root: {file_root}")
        # sys.argv = shlex.split(f"cmd {file_root}")
        sys.argv = f"{cmd} {file_root}".split(" ")
        args = parse_args()
        # test
        self.assertEqual(args.output, f"{file_root}.txt")

        # user specified output
        output_fn = "my_output.txt"
        # sys.argv = (f"{cmd} {file_root} -o {output_fn}"
        sys.argv = f"{cmd} {file_root} -o {output_fn}".split(" ")
        args = parse_args()
        self.assertEqual(args.output, output_fn)

    def test_output_overwrite(self):
        """Test that user cannot overwrite their output"""
        # tra file
        # tra file # again -> "error: output file already exists; use -f/--force to overwrite"
        # tra file -f/--force # overwrite
        # tra file -o output.txt # "error: output file already exists; use -f/--force to overwrite"
        # tra file -f -o output.txt # overwrite
        self.assertTrue(False)

    def test_compress(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        sys.argv = f"{cmd} {self.file_root}".split(" ")
        parse_args()
        self.assertTrue("not compressed" in captured_output.getvalue())

        captured_output = io.StringIO()
        sys.stdout = captured_output
        sys.argv = f"{cmd} {self.file_root} -c".split(" ")
        self.assertTrue("not" not in captured_output.getvalue())


"""
    def test_tomogram_origin(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output

        tomogram = f"{os.path.join(TEST_DATA, 'tomogram')}\emd_1305.map"
        self.assertTrue(os.path.exists(tomogram))

        sys.argv = f"{cmd} {self.file_root} -O {tomogram}".split(" ")
        parse_args()
        self.assertTrue("-162" in captured_output.getvalue())

    def test_tomogram_voxel_size(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        tomogram = f"{os.path.join(TEST_DATA, 'tomogram')}\emd_1305.map"
        sys.argv = f"{cmd} {self.file_root} -v {tomogram}".split(" ")
        parse_args()
        self.assertTrue("5.43" in captured_output.getvalue())
"""


class TestAverage(unittest.TestCase):

    def test_motl(self):
        average_em = f"{os.path.join(TEST_DATA, 'motl')}/emd_10752.map"
        average = motl_a.Average(average_em)
        self.assertTrue(np.allclose(np.array(average.voxel_size), np.array((1.78, 1.78, 1.78))))
        self.assertEqual(average.nc, 160)
        self.assertEqual(average.nr, 160)
        self.assertEqual(average.ns, 160)
        self.assertEqual(average.origin, (0, 0, 0))
        self.assertEqual(average.mode, 2)
        self.assertTrue(average.encoded_data.startswith("AAAAAAAAA"))

        # test zlib compression
        data_binary = base64.b64decode(average.encoded_data_compressed)[:4]
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

    def test_dynamo(self):
        average_em = f"{os.path.join(TEST_DATA, 'dynamo')}/sample.em"
        if platform.system() == "Windows":
            average_em = os.path.normcase(average_em)
        average = dynamo_a.Average(average_em)
        self.assertEqual(average.nc, 40)
        self.assertEqual(average.nr, 40)
        self.assertEqual(average.ns, 40)
        self.assertEqual(average.mode, 2)
        self.assertTrue(average.encoded_data.startswith("6wVsv0vjKr"))

        # test zlib compression
        data_binary = base64.b64decode(average.encoded_data_compressed)[:4]
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

    def test_peet(self):
        self.assertTrue(False)


class Test_read_table(unittest.TestCase):
    def setUp(self) -> None:
        self.table_em = f"{os.path.join(TEST_DATA, 'motl')}/motl_bin4_clathin_ref12_tomo_2.em"
        self.table_tbl = f"{os.path.join(TEST_DATA, 'dynamo')}/emd_1305_averaged.tbl"
        # self.table_mod = f"{os.path.join(TEST_DATA, 'peet')}/sample"

        if platform.system() == "Windows":
            self.table_em = os.path.normcase(self.table_em)
            self.table_tbl = os.path.normcase(self.table_tbl)
            # self.table_mod = os.path.normcase(self.table_mod)

    def test_read_table(self):
        """Test that Read_table class reads table files correctly"""
        self.assertTrue(os.path.exists(self.table_em))
        self.assertTrue(os.path.exists(self.table_tbl))
        # self.assertTrue(os.path.exists(self.table_mod))

        captured_output = io.StringIO()
        sys.stdout = captured_output
        dynamo_table = utils.ReadTable(self.table_tbl)
        self.assertEqual(20, dynamo_table.rows)
        self.assertEqual(35, dynamo_table.cols)
        self.assertTrue("Dynamo" in captured_output.getvalue())

        captured_output = io.StringIO()
        sys.stdout = captured_output
        motl_table = utils.ReadTable(self.table_em)
        self.assertEqual(20, motl_table.cols)
        self.assertEqual(777, motl_table.rows)
        self.assertTrue("Briggs" in captured_output.getvalue())

        fake_table = f"{os.path.join(TEST_DATA, 'dynamo')}/dynamo_fake.tbl"
        if platform.system() == "Windows":
            fake_table = os.path.normcase(fake_table)

        with self.assertRaises(ValueError):
            ReadTable(fake_table)


class TestTable(unittest.TestCase):
    def test_motl(self):
        # table_em = f"{os.path.join(TEST_DATA, 'motl')}/motl_bin4_clathin_ref12_tomo_2.em"
        table_em = f"{os.path.join(TEST_DATA, 'motl')}/sample.em"
        table = utils.ReadTable(table_em)
        i = random.randint(0, len(table.col_data))
        print("random row number: " + str(i))
        data = table[i]
        print("content of the row: " + str(data))
        motl_row = motl_t.Table(data)

        self.assertTrue(-2 * math.pi <= motl_row.tdrot <= 2 * math.pi)
        self.assertTrue(-2 * math.pi <= motl_row.tilt <= 2 * math.pi)
        self.assertTrue(-2 * math.pi <= motl_row.narot <= 2 * math.pi)
        self.assertTrue(type(motl_row.x) == float)
        self.assertTrue(type(motl_row.y) == float)
        self.assertTrue(type(motl_row.z) == float)
        # print(motl_row.dx)

        # test that rotation is correct
        matrix_z_1 = np.array([
            [math.cos(motl_row.tdrot), -math.sin(motl_row.tdrot), 0],
            [math.sin(motl_row.tdrot), math.cos(motl_row.tdrot), 0],
            [0, 0, 1]
        ])

        matrix_x = np.array([
            [1, 0, 0],
            [0, math.cos(motl_row.tilt), -math.sin(motl_row.tilt)],
            [0, math.sin(motl_row.tilt), math.cos(motl_row.tilt)]
        ])

        matrix_z_2 = np.array([
            [math.cos(motl_row.narot), -math.sin(motl_row.narot), 0],
            [math.sin(motl_row.narot), math.cos(motl_row.narot), 0],
            [0, 0, 1]
        ])

        expect_r = matrix_z_1.dot(matrix_x).dot(matrix_z_2)
        actual_r = motl_row.transformation[:, 0:3]
        self.assertTrue(np.allclose(expect_r, actual_r))

        # test translation is correct
        expect_tx = np.array([data[7] + data[10], data[8] + data[11], data[9] + data[12]])
        actual_tx = motl_row.transformation[:, 3]
        print(actual_tx)
        print(expect_tx)
        self.assertTrue(np.allclose(expect_tx, actual_tx))

    def test_dynamo(self):
        table_tbl = f"{os.path.join(TEST_DATA, 'dynamo')}/sample.tbl"
        table = utils.ReadTable(table_tbl)
        i = random.randint(0, len(table.col_data))
        print("random row number: " + str(i))
        data = table[i]
        print("content of the row: " + str(data))
        dynamo_row = dynamo_t.Table(data)

        self.assertTrue(-360 <= dynamo_row.narot <= 360)
        self.assertTrue(-360 <= dynamo_row.tdrot <= 360)
        self.assertTrue(-360 <= dynamo_row.tilt <= 360)
        self.assertTrue(type(dynamo_row.x) == float)
        self.assertTrue(type(dynamo_row.y) == float)
        self.assertTrue(type(dynamo_row.z) == float)

        matrix_z_1 = np.array([
            [math.cos(dynamo_row.tdrot), math.sin(dynamo_row.tdrot), 0],
            [-math.sin(dynamo_row.tdrot), math.cos(dynamo_row.tdrot), 0],
            [0, 0, 1]
        ])

        matrix_x = np.array([
            [1, 0, 0],
            [0, math.cos(dynamo_row.tilt), math.sin(dynamo_row.tilt)],
            [0, -math.sin(dynamo_row.tilt), math.cos(dynamo_row.tilt)]
        ])

        matrix_z_2 = np.array([
            [math.cos(dynamo_row.narot), math.sin(dynamo_row.narot), 0],
            [-math.sin(dynamo_row.narot), math.cos(dynamo_row.narot), 0],
            [0, 0, 1]
        ])

        expect_r = matrix_z_1.dot(matrix_x).dot(matrix_z_2)
        actual_r = dynamo_row.transformation[:, 0:3]
        self.assertTrue(np.allclose(expect_r, actual_r))

        # test translation is correct
        expect_tx = np.array(
            [float(data[23]) + float(data[3]), float(data[24]) + float(data[4]), float(data[25]) + float(data[5])])
        actual_tx = dynamo_row.transformation[:, 3]
        self.assertTrue(np.allclose(expect_tx, actual_tx))

    def test_peet(self):
        # -> peet.Table
        self.assertTrue(False)


class TestOutput(unittest.TestCase):
    def test_output_name(self):
        file_root = f"{os.path.join(TEST_DATA, 'motl')}/sample"
        if platform.system() == "Windows":
            file_root = os.path.normcase(file_root)
        sys.argv = f"{cmd} {file_root}".split(" ")
        args = parse_args()
        avg = core_modules.get_average(args)
        tbl = utils.ReadTable(args.table)
        core_modules.get_output(avg, tbl, args)
        # core_modules.main() # todo: fix sys.exit(0) for windows
        output_fn = f"{os.path.join(TEST_DATA, 'motl')}/sample.txt"
        if platform.system() == "Windows":
            output_fn = os.path.normcase(output_fn)
        self.assertTrue(os.path.exists(output_fn))

    def test_transformations(self):
        self.assertTrue(False)

    def test_output_compression(self):
        self.assertTrue(False)

    def test_file_rename(self):
        # todo: or rename
        file_root = f"{os.path.join(TEST_DATA, 'motl')}/sample"
        if platform.system() == "Windows":
            file_root = os.path.normcase(file_root)
        sys.argv = f"{cmd} {file_root}".split(" ")
        args = parse_args()
        print(args.output)
        avg = core_modules.get_average(args)
        tbl = utils.ReadTable(args.table)
        core_modules.get_output(avg, tbl, args)
        # core_modules.main() # todo: fix sys.exit(0) for windows
        output_fn = f"{os.path.join(TEST_DATA, 'motl')}/sample(1).txt"
        if platform.system() == "Windows":
            output_fn = os.path.normcase(output_fn)
        self.assertTrue(os.path.exists(output_fn))


class TestCoreModules(unittest.TestCase):

    def test_motl(self):
        # tra file # file is a motl .em, .map
        self.file_root = f"{os.path.join(TEST_DATA, 'motl')}/sample"
        if platform.system() == "Windows":
            self.file_root = os.path.normcase(self.file_root)

        sys.argv = f"{cmd} {self.file_root}".split(" ")
        args = parse_args()
        cls_average = core_modules.get_average(args)
        cls_table_file = utils.ReadTable(args.table)
        cls_table = core_modules.get_table(args, cls_table_file[random.randint(0, cls_table_file.rows)])
        # todo: better structure of ReadTable + core_modules.get_table?

        self.assertIsInstance(cls_average, motl_a.Average)
        self.assertIsInstance(cls_table, motl_t.Table)

    def test_dynamo(self):
        self.file_root = f"{os.path.join(TEST_DATA, 'dynamo')}/sample"
        if platform.system() == "Windows":
            self.file_root = os.path.normcase(self.file_root)

        sys.argv = f"{cmd} {self.file_root}".split(" ")
        print(sys.argv)
        args = parse_args()

        cls_average = core_modules.get_average(args)
        cls_table_file = utils.ReadTable(args.table)
        cls_table = core_modules.get_table(args, cls_table_file[random.randint(0, cls_table_file.rows)])
        # todo: better structure of ReadTable + core_modules.get_table?
        self.assertIsInstance(cls_average, dynamo_a.Average)
        self.assertIsInstance(cls_table, dynamo_t.Table)
