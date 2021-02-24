import argparse
import os
import sys
import pathlib
import platform

parser = argparse.ArgumentParser(prog='cmd', description='Generic structure of sta')
parser.add_argument('file', nargs="?")
parser.add_argument('-T', '--table', help='table of coordinates')
parser.add_argument('-A', '--average', help='averaged density')
# parser.add_argument('-t', '--tomogram', help=f"the tomogram")
parser.add_argument("-o", "--output", help="the output file name (.txt)")
parser.add_argument("-c", "--compress", default=False, action="store_true",
                    help="Compress the voxel data [default: False]")
#parser.add_argument("-O", "--tomogram-origin",
#                    help="Print the nxstart, nystart, nzstart of the tomogram file in the x, y, z directions. Currently support .map and .mrc format")
#parser.add_argument("-v", "--voxel-size",
#                    help="Print the voxel-size of the tomogram file in the x, y, z directions. Currently support .map and .mrc")
# todo

def _check_file_types(args):
    """returns indicator of which file type"""
    if os.path.exists(f"{args.file}.em") and os.path.exists(f"{args.file}.map"):  # Motl
        return 0
    elif os.path.exists(f"{args.file}.tbl") and os.path.exists(f"{args.file}.em"):  # Dynamo
        return 1
    elif os.path.exists(f"{args.file}.mod") and os.path.exists(f"{args.file}.rec"):  # Briggs
        return 2
    else:
        return -1


def parse_args():
    """Sanity checks on arguments"""
    args = parser.parse_args()
    if args.file:
        if platform.system() == "Windows":
            args.file = args.file.replace(os.sep, "\\")
        else:
            args.file = args.file.replace(os.sep, "/")
        # check for the presence of different file type s
        file_type = _check_file_types(args)
        # assuming Brigg's data
        if file_type == 0:
            args.table = f"{args.file}.em"
            args.average = f"{args.file}.map"
        elif file_type == 1:
            args.table = f"{args.file}.tbl"
            args.average = f"{args.file}.em"
        elif file_type == 2:
            args.table = f"{args.file}.mod"
            args.average = f"{args.file}.rec"
        else:
            print(f"indeterminate file types: {file_type}", file=sys.stderr)
            print(f"please ensure that {args.file}.<table extension> and {args.file}.<average extension> exist",
                  file=sys.stderr)
            print(f"alternatively, use -T/--table <file> -A/--average <file> to run", file=sys.stderr)
            return None  # os.EX_USAGE
    else:
        try:
            assert args.table and args.average
        except AssertionError:
            print(f"both -T/--table and -A/--average must be used together", file=sys.stderr)
            # sys.exit(1)  # os.EX_USAGE
            return None
    # we are guaranteed we have reliable and consistent args

    if not args.output:
        args.output = f"{args.file}.txt"
    else:
        assert args.output

    if args.compress:
        # print("Output encoded voxel data is compressed.")
        print(f"{args.output} is created, volume data is compressed.")
    else:
        # print("Output encoded voxel data is not compressed.")
        print(f"{args.output} is created, volume data is not compressed.")

#    if args.tomogram_origin:
#        import mrcfile
#        with mrcfile.open(args.tomogram_origin) as mrc:
#            start = int(mrc.header.nxstart), int(mrc.header.nystart), int(mrc.header.nzstart)
#            print(f"The map starts at {tuple(start)}.")

#    if args.voxel_size:
#        import mrcfile
#        with mrcfile.open(args.voxel_size) as mrc:
#            size = mrc.voxel_size
#            print(f"The voxel size of the tomogram is {size}.")

    return args
