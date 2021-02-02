import shlex
import sys
import unittest
import os
import pathlib
import platform

from .. import TEST_DATA
from ..parser import parse_args


class TestCLI(unittest.TestCase):
    def test_default(self):
        file_root = f"{os.path.join(TEST_DATA, 'motl')}/file"
        print(file_root)
        if platform.system() == "Windows":
            file_root = os.path.normcase(file_root)
        print(f"value of file_root: {file_root}")
        # sys.argv = shlex.split(f"cmd {file_root}")
        sys.argv = f"cmd {file_root}".split(" ")
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
        sys.argv = shlex.split(f"cmd -T {file_root}.em -A {file_root}.map")
        print(sys.argv)
        args = parse_args()
        print(args)

