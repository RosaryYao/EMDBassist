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
        return motl_t.Table(table)
    if re.match(r".*\.em$", args.average) and re.match(r".*\.tbl$", args.table):
        return dynamo_t.Table(table)
    # elif re.match(r".*\.rec$", args.average) and re.match(r".*\.mod$", args.table):
    #    return peet_t.Average(args.average)
    else:
        print(f"unknown table format '{args.table}'", file=sys.stderr)


def get_output(avg, tbl, args):
    """Factory function which returns appropriate Output class"""
    #average = get_average(args.average)
    #table = utils.ReadTable(args.table)
    output_fn = args.output
    output_fn_root = re.sub(r'.txt$', "", output_fn)

    output_transformations = []
    for i in range(0, tbl.rows):
        transformation = get_table(args, tbl[i]).transformation
        output_transformations.append(transformation)

    # todo： overwrite file if file already exist?
    # if os.path.exists(output_fn):
    #    os.remove(output_fn)

    # todo: or rename the file?
    rename_flag = 0
    while os.path.exists(output_fn):
        rename_flag += 1
        output_fn = f'{output_fn_root}({rename_flag}).txt'
        print('File already exists!')
        # print("New file name: " + output_fn)

    with open(output_fn, "w") as f:
        for i in range(tbl.rows):
            line_to_write = str(i + 1) + "," \
                            + "".join(
                str(f"{e},").replace("[", "").replace("]", "").replace(" ", "") for e in output_transformations[i]) \
                            + "0,0,0,1\n"
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
    tbl = utils.ReadTable(args.table)
    # create a generic output object
    # out = get_output(avg, tbl, args)
    # write the output
    # out.write()
    # output_txt(args)
    get_output(avg, tbl, args)
    return sys.exit(0)  # constants which inform the OS on exit status


if __name__ == "__main__":
    sys.exit(main())
