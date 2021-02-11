import io
import os
import platform
import sys
import unittest
from unittest import mock

from .. import TEST_DATA, core_modules
from ..average import motl
from ..table import motl, dynamo, peet
from ..utils import Read_table
from ..parser import parse_args

cmd = "tra"


class TestCLI(unittest.TestCase):
    def setUp(self) -> None:
        self.file_root = f"{os.path.join(TEST_DATA, 'motl')}/file"
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
        self.file_root = f"{os.path.join(TEST_DATA, 'dynamo')}/file"
        if platform.system() == "Windows":
            self.file_root = os.path.normcase(self.file_root)

        self.assertTrue(os.path.exists(f"{self.file_root}.tbl"))
        self.assertTrue(os.path.exists(f"{self.file_root}.em"))
        sys.argv = f"{cmd} {self.file_root}".split(" ")
        args = parse_args()
        self.assertEqual(args.table, f'{self.file_root}.tbl')
        self.assertEqual(args.average, f'{self.file_root}.em')

    def test_peet(self):
        self.file_root = f"{os.path.join(TEST_DATA, 'peet')}/file"
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
        file_root = f"{os.path.join(TEST_DATA, 'motl')}/file"  # windows' format
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
    def setUp(self) -> None:
        self.file_root = f"{os.path.join(TEST_DATA, 'motl')}/file"
        if platform.system() == "Windows":
            self.file_root = os.path.normcase(self.file_root)

    def test_motl(self):
        # tra file # file is a motl .em, .map
        sys.argv = f"{cmd} {self.file_root}".split(" ")
        args = parse_args()
        cls = core_modules.get_average(args)
        self.assertIsInstance(cls, motl.Average)

    def test_dynamo(self):
        self.assertTrue(False)

    def test_peet(self):
        self.assertTrue(False)


class TestTable(unittest.TestCase):
    def setUp(self) -> None:
        self.table_em = f"{os.path.join(TEST_DATA, 'motl')}/motl_bin4_clathin_ref12_tomo_2.em"
        self.table_tbl = f"{os.path.join(TEST_DATA, 'dynamo')}/emd_1305_averaged.tbl"
        # self.table_mod = f"{os.path.join(TEST_DATA, 'peet')}/file"

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
        dynamo_table = Read_table(self.table_tbl)
        self.assertEqual(20, dynamo_table.rows)
        self.assertEqual(35, dynamo_table.cols)
        self.assertTrue("Dynamo" in captured_output.getvalue())

        captured_output = io.StringIO()
        sys.stdout = captured_output
        motl_table = Read_table(self.table_em)
        self.assertEqual(20, motl_table.cols)
        self.assertEqual(777, motl_table.rows)
        self.assertTrue("Briggs" in captured_output.getvalue())

    def test_motl(self):
        # -> motl.Table
        self.assertTrue(False)

    def test_dynamo(self):
        # -> dynamo.Table
        self.assertTrue(False)

    def test_peet(self):
        # -> peet.Table
        self.assertTrue(False)
