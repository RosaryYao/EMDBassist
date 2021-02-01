import argparse
import os
import sys

parser = argparse.ArgumentParser(prog='cmd', description='Generic structure of sta')
parser.add_argument('file')
parser.add_argument('-T', '--table', help='table of coordinates')
parser.add_argument('-A', '--average', help='averaged density')


def _check_file_types(args):
    """returns indicator of which file type"""
    if os.path.exists(f"{args.file}.em") and os.path.exists(f"{args.file}.map"):  # Briggs
        return 0
    elif os.path.exists(f"./{args.file}.tbl") and os.path.exists(f"./{args.file}.em"):  # Dynamo
        return 1
    elif os.path.exists(f"./{args.file}.mod") and os.path.exists(f"./{args.file}.rec"):  # PEET
        return 2
    else:
        return -1


def parse_args():
    args = parser.parse_args()
    if args.file:
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
            print(f"indeterminate file types", file=sys.stderr)
            print(f"please ensure that {args.file}.<table extension> and {args.file}.<average extension> exist",
                  file=sys.stderr)
            print(f"alternatively, use -T/--table <file> -A/--average <file> to run", file=sys.stderr)
            sys.exit(os.EX_USAGE)
    return args
