"""
The script that runs the modules, and output the text file?
Also, it ignores calculation using data from tomograms
"""
import os
import re
import sys

from new_main import TEST_DATA, parser
from new_main.average import motl as motl_a
# todo: change motl_a into average.motl etc.
from new_main import average, table

from new_main.average import dynamo as dynamo_a
from new_main.average import peet as peet_a
# from new_main.average.motl import Brigg_map as brigg_sta
from new_main.table import motl as motl_t
from new_main.table import dynamo as dynamo_t
from new_main.table import peet as peet_t
# from new_main.table.motl import MotlRow as brigg_tbl
# from new_main.table.dynamo import TblRow as dynamo_tbl
from new_main import utils

motl_data = os.path.join(TEST_DATA, 'motl', 'file.txt')

with open(motl_data) as _:  # todo: what is this?
    print(_.read())


def get_average(args):
    """Factory function which returns appropriate Average class"""
    if re.match(r".*\.map$", args.average) and re.match(r".*\.em$", args.table):
        return motl_a.Average(args)
    elif re.match(r".*\.em$", args.average) and re.match(r".*\.tbl$", args.table):
        return dynamo_a.Average(args.average)  # todo: change the interface, takes args in addition for modification
    # elif re.match(r".*\.rec$", args.average) and re.match(r".*\.mod$", args.table):
    #    return peet_a.Average(args.average)
    else:
        print(f"unknown average format '{args.average}'", file=sys.stderr)


def get_table(args, table):
    """Factory function which returns appropriate Table class"""
    # todo: better structure of ReadTable + core_modules.get_table?

    if re.match(r".*\.map$", args.average) and re.match(r".*\.em$", args.table):
        return motl_t._Table(table)
    if re.match(r".*\.em$", args.average) and re.match(r".*\.tbl$", args.table):
        return dynamo_t.Table(table)
    # elif re.match(r".*\.rec$", args.average) and re.match(r".*\.mod$", args.table):
    #    return peet_t.Average(args.average)
    else:
        print(f"unknown table format '{args.table}'", file=sys.stderr)


def get_output(avg, tbl, args):
    """To be factory function which returns appropriate Output class"""
    with open(args.output, "w") as f:
        for i, table_row in enumerate(tbl):
            # fixme: fix
            # line_to_write = f"{}," \
            #                 + "".join(
            #     str(f"{e},") for e in output_transformations[i]) \
            #                 + "0,0,0,1\n"
            line_to_write = f"{i + 1}\t{table_row}\n"
            f.write(line_to_write)

        f.write("Mode:" + "\t" + str(avg.mode) + "\n")
        f.write("Nc:" + "\t" + str(avg.nc) + "\n")
        f.write("Nr:" + "\t" + str(avg.nr) + "\n")
        f.write("Ns:" + "\t" + str(avg.ns) + "\n")

        if args.compress:
            # compress_flag = 1
            f.write(avg.encoded_data_compressed)
            print(f"{output_fn} is created, volume data is compressed.")
        else:
            # compress_flag = 0
            f.write(avg.encoded_data)
            print(f"{output_fn} is created, volume data is not compressed.")

def main():
    args = parser.parse_args()
    # create the generic average object
    avg = get_average(args)
    # create the generic table object
    tbl = utils.Table(args.table)
    # create a generic output object
    # out = get_output(avg, tbl, args)
    # write the output
    # out.write()
    # output_txt(args)
    get_output(avg, tbl, args)
    return sys.exit(0)  # constants which inform the OS on exit status


if __name__ == "__main__":
    sys.exit(main())
