import base64
import binascii
import io
import math
import os
import platform
import random
import re
import sys
import unittest

import numpy as np

from .. import average, table
from .. import TEST_DATA, core_modules, utils
from ..average import dynamo as dynamo_a
from ..average import motl as motl_a
from ..parser import parse_args
from ..table import dynamo as dynamo_t
from ..table import motl as motl_t
# from . import parser, average, table

cmd = "tra"


class TestCLI(unittest.TestCase):
    def setUp(self) -> None:
        self.motl_fn_root = os.path.join(TEST_DATA, 'motl', 'file')
        self.dynamo_fn_root = os.path.join(TEST_DATA, 'dynamo', 'file')
        self.peet_fn_root = os.path.join(TEST_DATA, 'peet', 'file')
        #if platform.system() == "Windows":
        #    self.motl_fn_root = os.path.normcase(self.motl_fn_root)
        #    self.dynamo_fn_root = os.path.normcase(self.dynamo_fn_root)
        #    self.peet_fn_root = os.path.normcase(self.peet_fn_root)

    def test_default(self):
        sys.argv = f"{cmd} {self.motl_fn_root}".split(" ")
        args = parse_args()
        self.assertEqual(args.file, self.motl_fn_root)
        self.assertEqual(args.table, f"{self.motl_fn_root}.em")
        self.assertEqual(args.average, f"{self.motl_fn_root}.map")

    def test_explicit(self):
        """User explicitly specifies files"""
        sys.argv = f"{cmd} -T {self.motl_fn_root}.em -A {self.motl_fn_root}.map".split(" ")
        args = parse_args()
        self.assertEqual(args.table, f"{self.motl_fn_root}.em")
        self.assertEqual(args.average, f"{self.motl_fn_root}.map")

        # ensure AssertionError raised when only one specified file given
        sys.argv = f"cmd -T {self.motl_fn_root}.em".split(" ")
        args = parse_args()
        self.assertIsNone(args)

    def test_dynamo(self):
        self.assertTrue(os.path.exists(f"{self.dynamo_fn_root}.tbl"))
        self.assertTrue(os.path.exists(f"{self.dynamo_fn_root}.em"))
        sys.argv = f"{cmd} {self.dynamo_fn_root}".split(" ")
        args = parse_args()
        self.assertEqual(args.table, f'{self.dynamo_fn_root}.tbl')
        self.assertEqual(args.average, f'{self.dynamo_fn_root}.em')

    def test_peet(self):
        self.assertTrue(os.path.exists(f"{self.peet_fn_root}.rec"))
        self.assertTrue(os.path.exists(f"{self.peet_fn_root}.mod"))
        sys.argv = f"{cmd} {self.peet_fn_root}".split(" ")
        args = parse_args()
        self.assertEqual(args.table, f'{self.peet_fn_root}.mod')
        self.assertEqual(args.average, f'{self.peet_fn_root}.rec')

    def test_output(self):
        """Ensure that output is handled correctly"""
        sys.argv = f"{cmd} {self.motl_fn_root}".split(" ")
        args = parse_args()
        self.assertEqual(args.output, f"{self.motl_fn_root}.txt")
        # user specified output
        output_fn = "my_output.txt"
        sys.argv = f"{cmd} {self.motl_fn_root} -o {output_fn}".split(" ")
        args = parse_args()
        self.assertEqual(args.output, output_fn)

        avg_fn = os.path.join(TEST_DATA, 'motl', 'unknown_format.am')
        tbl_fn = os.path.join(TEST_DATA, 'motl', 'unknown_format.col')
        sys.argv = f"{cmd} -A {avg_fn} -T {tbl_fn} -f".split(' ')
        args = parse_args()
        self.assertEqual(args.output, os.path.join(TEST_DATA, 'motl', 'unknown_format.txt'))

    def test_output_overwrite(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        output_fn = os.path.join(TEST_DATA, 'motl', 'test_rewrite.txt')
        sys.argv = f"{cmd} {self.motl_fn_root} -o {output_fn}".split(" ")

        with self.assertRaises(FileExistsError):
            parse_args()
            self.assertTrue("already exists" in captured_output.getvalue())

    def test_output_overwrite_force(self):
        """Test that user cannot overwrite their output"""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        output_fn = os.path.join(TEST_DATA, 'motl', 'test_rewrite.txt')
        sys.argv = f"{cmd} {self.motl_fn_root} -o {output_fn} -f".split(" ")
        args = parse_args()
        self.assertTrue("overwritten" in captured_output.getvalue())

    def test_compress(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        sys.argv = f"{cmd} {self.motl_fn_root}".split(" ")
        parse_args()
        self.assertTrue("not compressed" in captured_output.getvalue())

        captured_output = io.StringIO()
        sys.stdout = captured_output
        sys.argv = f"{cmd} {self.motl_fn_root} -c".split(" ")
        self.assertTrue("not" not in captured_output.getvalue())

    def test_verbose(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        sys.argv = f"{cmd} {self.motl_fn_root} -v -f".split(" ")
        parse_args()
        self.assertTrue("verbose" in captured_output.getvalue())


class TestAverage(unittest.TestCase):
    def setUp(self) -> None:
        self.motl_fn_root = os.path.join(TEST_DATA, 'motl', 'file')
        self.dynamo_fn_root = os.path.join(TEST_DATA, 'dynamo', 'file')
        self.peet_fn_root = os.path.join(TEST_DATA, 'peet', 'file')
        if platform.system() == "Windows":
            self.motl_fn_root = os.path.normcase(self.motl_fn_root)
            self.dynamo_fn_root = os.path.normcase(self.dynamo_fn_root)
            self.peet_fn_root = os.path.normcase(self.peet_fn_root)

    def test_motl(self):
        sys.argv = f"{cmd} {os.path.join(TEST_DATA, 'motl', 'emd_12132')}".split(' ')
        args = parse_args()
        avg = average.motl.Average(args.average, args)
        self.assertTrue(np.allclose(np.array(avg.voxel_size), np.array((7.08, 7.08, 7.08))))
        self.assertEqual(avg.nc, 50)
        self.assertEqual(avg.nr, 50)
        self.assertEqual(avg.ns, 50)
        self.assertEqual(avg.origin, (0, 0, 0))
        self.assertEqual(avg.mode, 2)
        self.assertTrue(avg.encoded_data.startswith("7CigvyDAmL/JA1O/FIe1vjkme"))

        # test zlib compression
        data_binary = base64.b64decode(avg.encoded_data_compressed)[:4]
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
        sys.argv = f"{cmd} {os.path.join(TEST_DATA, average_em)}".split(' ')
        args = parse_args()

        avg = average.dynamo.Average(average_em, args)
        self.assertEqual(avg.nc, 40)
        self.assertEqual(avg.nr, 40)
        self.assertEqual(avg.ns, 40)
        self.assertEqual(avg.mode, 2)
        self.assertTrue(avg.encoded_data.startswith("6wVsv0vjKr"))

        # test zlib compression
        data_binary = base64.b64decode(avg.encoded_data_compressed)[:4]
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

    def test_unknown_format(self):
        avg_fn = os.path.join(TEST_DATA, 'motl', 'unknown_format.am')
        tbl_fn = os.path.join(TEST_DATA, 'motl', 'unknown_format.col')
        sys.argv = f"{cmd} -A {avg_fn} -T {tbl_fn} -f".split(' ')
        args = parse_args()
        with self.assertRaises(TypeError):
            core_modules.get_average(args)
        with self.assertRaises(TypeError):
            core_modules.get_table(args)


class TestTable(unittest.TestCase):
    def test_table_dynamo(self):
        """Test that Read_table class reads table files correctly"""

        # Dynamo
        self.avg = f"{os.path.join(TEST_DATA, 'dynamo')}/sample.em"
        self.tbl = f"{os.path.join(TEST_DATA, 'dynamo')}/sample.tbl"
        if platform.system() == "Windows":
            self.avg = os.path.normcase(self.avg)
            self.tbl = os.path.normcase(self.tbl)
        self.assertTrue(os.path.exists(self.avg))
        self.assertTrue(os.path.exists(self.tbl))

        sys.argv = f"{cmd} -A {self.avg} -T {self.tbl} -f".split(' ')
        args = parse_args()
        dynamo_table = table.dynamo.Table(self.tbl, args)
        self.assertEqual(20, dynamo_table.rows)
        self.assertEqual(35, dynamo_table.cols)

    def test_table_brigg(self):
        self.avg = f"{os.path.join(TEST_DATA, 'motl')}/sample.map"
        self.tbl = f"{os.path.join(TEST_DATA, 'motl')}/sample.em"
        if platform.system() == "Windows":
            self.avg = os.path.normcase(self.avg)
            self.tbl = os.path.normcase(self.tbl)
        self.assertTrue(os.path.exists(self.avg))
        self.assertTrue(os.path.exists(self.tbl))

        sys.argv = f"{cmd} -A {self.avg} -T {self.tbl} -f".split(' ')
        args = parse_args()
        motl_table = table.motl.Table(self.tbl, args)
        self.assertEqual(20, motl_table.cols)
        self.assertEqual(777, motl_table.rows)

    def test_wrong_dimension(self):
        # Fake table - with different number of elements in any rows
        self.avg = f"{os.path.join(TEST_DATA, 'dynamo')}/sample.em"
        self.fake_tbl = f"{os.path.join(TEST_DATA, 'dynamo')}/dynamo_fake.tbl"
        sys.argv = f"{cmd} -A {self.avg} -T {self.fake_tbl} -f".split(' ')
        args = parse_args()
        if platform.system() == "Windows":
            self.fake_tbl = os.path.normcase(self.fake_tbl)

        with self.assertRaises(ValueError):
            table.dynamo.Table(self.fake_tbl, args)


class Test_TableRow(unittest.TestCase):
    def test_motl(self):
        file_root = f"{os.path.join(TEST_DATA, 'motl')}/sample"
        sys.argv = f"{cmd} {file_root} -f".split(" ")
        args = parse_args()
        os.path.exists(args.average)
        os.path.exists(args.table)

        tbl = core_modules.get_table(args)
        self.assertIsInstance(tbl, table.motl.Table)

        i = random.randint(0, tbl.rows-1)
        motl_row = tbl[i]

        self.assertTrue(-2 * math.pi <= motl_row.tdrot <= 2 * math.pi)
        self.assertTrue(-2 * math.pi <= motl_row.tilt <= 2 * math.pi)
        self.assertTrue(-2 * math.pi <= motl_row.narot <= 2 * math.pi)
        self.assertTrue(type(motl_row.x) == float)
        self.assertTrue(type(motl_row.y) == float)
        self.assertTrue(type(motl_row.z) == float)

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
        data = tbl.col_data[i]
        expect_tx = np.array([data[7] + data[10], data[8] + data[11], data[9] + data[12]])
        actual_tx = motl_row.transformation[:, 3]
        self.assertTrue(np.allclose(expect_tx, actual_tx))

    def test_dynamo(self):
        file_root = f"{os.path.join(TEST_DATA, 'dynamo')}/sample"
        sys.argv = f"{cmd} {file_root}".split(" ")
        args = parse_args()
        os.path.exists(args.average)
        os.path.exists(args.table)

        tbl = core_modules.get_table(args)
        self.assertIsInstance(tbl, dynamo_t.Table)

        i = random.randint(0, tbl.rows - 1)
        tbl_row = tbl[i]

        self.assertTrue(-2 * math.pi <= tbl_row.tdrot <= 2 * math.pi)
        self.assertTrue(-2 * math.pi <= tbl_row.tilt <= 2 * math.pi)
        self.assertTrue(-2 * math.pi <= tbl_row.narot <= 2 * math.pi)
        self.assertTrue(type(tbl_row.x) == float)
        self.assertTrue(type(tbl_row.y) == float)
        self.assertTrue(type(tbl_row.z) == float)

        matrix_z_1 = np.array([
            [math.cos(tbl_row.tdrot), math.sin(tbl_row.tdrot), 0],
            [-math.sin(tbl_row.tdrot), math.cos(tbl_row.tdrot), 0],
            [0, 0, 1]
        ])

        matrix_x = np.array([
            [1, 0, 0],
            [0, math.cos(tbl_row.tilt), math.sin(tbl_row.tilt)],
            [0, -math.sin(tbl_row.tilt), math.cos(tbl_row.tilt)]
        ])

        matrix_z_2 = np.array([
            [math.cos(tbl_row.narot), math.sin(tbl_row.narot), 0],
            [-math.sin(tbl_row.narot), math.cos(tbl_row.narot), 0],
            [0, 0, 1]
        ])

        expect_r = matrix_z_1.dot(matrix_x).dot(matrix_z_2)
        actual_r = tbl_row.transformation[:, 0:3]
        self.assertTrue(np.allclose(expect_r, actual_r))

        # test translation is correct
        data = tbl.col_data[i]
        expect_tx = np.array(
            [float(data[23]) + float(data[3]), float(data[24]) + float(data[4]), float(data[25]) + float(data[5])])
        actual_tx = tbl_row.transformation[:, 3]
        self.assertTrue(np.allclose(expect_tx, actual_tx))

    def test_peet(self):
        # -> peet.Table
        self.assertTrue(False)


class TestCoreModules(unittest.TestCase):
    def test_motl(self):
        # tra file # file is a motl .em, .map
        self.file_root = f"{os.path.join(TEST_DATA, 'motl')}/sample"
        if platform.system() == "Windows":
            self.file_root = os.path.normcase(self.file_root)

        sys.argv = f"{cmd} {self.file_root} -f".split(" ")
        args = parse_args()
        avg = core_modules.get_average(args)
        tbl = core_modules.get_table(args)

        self.assertIsInstance(avg, average.motl.Average)
        self.assertIsInstance(tbl, table.motl.Table)

    def test_get_average(self):
        brigg_root = f"{os.path.join(TEST_DATA, 'motl')}/sample"
        sys.argv = f"{cmd} {brigg_root} -f".split(" ")
        args = parse_args()
        avg = core_modules.get_average(args)
        self.assertIsInstance(avg, average.motl.Average)

        # if args.verbose
        captured_output = io.StringIO()
        sys.stdout = captured_output
        sys.argv = f"{cmd} {brigg_root} -f -v".split(" ")
        args = parse_args()
        core_modules.get_average(args)
        if args.verbose:
            self.assertTrue("Briggs'" in captured_output.getvalue())

        dynamo_root = f"{os.path.join(TEST_DATA, 'dynamo')}/sample"
        sys.argv = f"{cmd} {brigg_root} -f".split(" ")
        args = parse_args()
        avg = core_modules.get_average(args)
        self.assertIsInstance(avg, average.motl.Average)
        # if args.verbose
        captured_output = io.StringIO()
        sys.stdout = captured_output
        sys.argv = f"{cmd} {dynamo_root} -f -v".split(" ")
        args = parse_args()
        core_modules.get_average(args)
        if args.verbose:
            self.assertTrue("Dynamo" in captured_output.getvalue())

    def test_dynamo(self):
        self.file_root = f"{os.path.join(TEST_DATA, 'dynamo')}/sample"
        if platform.system() == "Windows":
            self.file_root = os.path.normcase(self.file_root)

        sys.argv = f"{cmd} {self.file_root} -f".split(" ")
        args = parse_args()

        avg = core_modules.get_average(args)
        tbl = core_modules.get_table(args)
        self.assertIsInstance(avg, average.dynamo.Average)
        self.assertIsInstance(tbl, table.dynamo.Table)

    # test get_output()
    def test_output_name(self):
        file_root = f"{os.path.join(TEST_DATA, 'motl')}/sample"
        if platform.system() == "Windows":
            file_root = os.path.normcase(file_root)
        sys.argv = f"{cmd} {file_root} -f".split(" ")
        args = parse_args()
        avg = core_modules.get_average(args)
        tbl = core_modules.get_table(args)
        core_modules.get_output(avg, tbl, args)
        output_fn = f"{os.path.join(TEST_DATA, 'motl')}/sample.txt"
        self.assertTrue(os.path.exists(output_fn))
        os.remove(output_fn)

    def test_transformations(self):
        file_root = f"{os.path.join(TEST_DATA, 'dynamo')}/sample"
        sys.argv = f"{cmd} {file_root}".split(" ")
        args = parse_args()
        avg = core_modules.get_average(args)
        tbl = core_modules.get_table(args)
        core_modules.get_output(avg, tbl, args)
        output_fn = f"{os.path.join(TEST_DATA, 'dynamo')}/sample.txt"
        if platform.system() == "Windows":
            output_fn = os.path.normcase(output_fn)

        with open(output_fn) as output:
            first_row = output.readline()
            transformation = first_row.split(",")
        self.assertEqual(len(transformation), 17)
        os.remove(output_fn)

    def test_output_volume_information(self):
        file_root = f"{os.path.join(TEST_DATA, 'dynamo')}/sample"
        sys.argv = f"{cmd} {file_root}".split(" ")
        args = parse_args()
        avg = core_modules.get_average(args)
        tbl = core_modules.get_table(args)
        core_modules.get_output(avg, tbl, args)
        # core_modules.main() # todo: fix sys.exit(0) for windows
        output_fn = f"{os.path.join(TEST_DATA, 'dynamo')}/sample.txt"

        with open(output_fn) as output:
            output_list = output.readlines()
            for each in output_list:
                if re.match(r"^Nc:", each):
                    nc = re.findall(r"\d+", each)
                    nc = int(nc[0])
                if re.match(r'^Nr', each):
                    nr = re.findall(r'\d+', each)
                    nr = int(nr[0])
                if re.match(r"^Ns:", each):
                    ns = re.findall(r"\d+", each)
                    ns = int(ns[0])
                if re.match(r"^Mode:", each):
                    mode = re.findall(r"\d+", each)
                    mode = int(mode[0])
        os.remove(output_fn)
        self.assertEqual(nc, 40)
        self.assertEqual(nr, 40)
        self.assertEqual(ns, 40)
        self.assertEqual(mode, 2)

    def test_output_uncompressed(self):  # todo: necessary?
        self.assertTrue(False)

    def test_output_compressed(self):  # todo: necessary?
        self.assertTrue(False)


