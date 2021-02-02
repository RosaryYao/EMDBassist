import os
import platform
import shlex
import sys
import unittest

from .. import TEST_DATA
from ..parser import parse_args

cmd = "tra"

class TestCLI(unittest.TestCase):
    def test_default(self):
        file_root = f"{os.path.join(TEST_DATA, 'motl')}/file"
        print(file_root)
        if platform.system() == "Windows":
            file_root = os.path.normcase(file_root)
        print(f"value of file_root: {file_root}")
        # sys.argv = shlex.split(f"cmd {file_root}")
        sys.argv = f"{cmd} {file_root}".split(" ")
        print(sys.argv)
        args = parse_args()
        print(f"The args.file is: {args.file}")
        print(os.path.exists(f"{args.file}.em"))
        print(os.path.exists(f"{file_root}.em"))
        self.assertEqual(args.file, file_root)
        self.assertEqual(args.table, f"{file_root}.em")
        self.assertEqual(args.average, f"{file_root}.map")

    def test_explicit(self):
        """User explicitly specifies files"""
        file_root = f"{os.path.join(TEST_DATA, 'motl')}/file"
        sys.argv = shlex.split(f"{cmd} -T {file_root}.em -A {file_root}.map")
        args = parse_args()
        self.assertEqual(args.table, f"{file_root}.em")
        self.assertEqual(args.average, f"{file_root}.map")
        # ensure
        sys.argv = shlex.split(f"cmd -T {file_root}.em")
        args = parse_args()
        self.assertEqual(args, os.EX_USAGE)

    def test_dynamo(self):
        self.assertTrue(False)

    def test_peet(self):
        self.assertTrue(False)

    def test_output(self):
        """Ensure that output is handled correctly"""
        sys.argv = shlex.split(f"{cmd} file") # output not specified
        args = parse_args()
        # test
        self.assertEqual(args.output, "")
        # user specified output
        output_fn = "my_output"
        sys.argv = shlex.split(f"{cmd} file -o {output_fn}")
        args = parse_args()
        self.assertEqual(args.output, output_fn)
