import shlex
import sys
import unittest
import os

from .. import TEST_DATA
from ..parser import parse_args


class TestCLI(unittest.TestCase):
    def test_default(self):
        file_root = f"{os.path.join(TEST_DATA, 'motl')}/file"
        sys.argv = shlex.split(f"cmd {file_root}")
        args = parse_args()
        print(args)
        self.assertEqual(args.table, f"{file_root}.em")
        self.assertEqual(args.average, f"{file_root}.map")

    def test_explicit(self):
        """User explicitly specifies files"""
        file_root = f"{os.path.join(TEST_DATA, 'motl')}/file"
        sys.argv = shlex.split(f"cmd -T {file_root}.em -A {file_root}.map")
        args = parse_args()
        print(args)

