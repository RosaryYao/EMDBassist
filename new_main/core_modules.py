"""
The script that runs the modules, and output the text file?
Also, it ignores calculation using data from tomograms
"""
import os
import re
import sys

from new_main import TEST_DATA, parser
from new_main.average import motl
from new_main.average import dynamo
# from new_main.average.motl import Brigg_map as brigg_sta
from new_main.table import motl
from new_main.table import dynamo
# from new_main.table.motl import MotlRow as brigg_tbl
# from new_main.table.dynamo import TblRow as dynamo_tbl
from new_main import utils

motl_data = os.path.join(TEST_DATA, 'motl', 'file.txt')

with open(motl_data) as _:  # todo: what is this?
    print(_.read())


def get_average(args):
    """Factory function which returns appropriate Average class"""
    if re.match(r".*\.map$", args.average) and re.match(r".*\.em$", args.table):
        return motl.Average(args)
    else:
        print(f"unknown average format '{args.average}'", file=sys.stderr)


def get_table(args):
    """Factory function which returns appropriate Table class"""
    if re.match(r".*\.map$", args.average) and re.match(r".*\.em$", args.table):
        return motl.Table(args)
    if re.match(r".*\.em$", args.average) and re.match(r".*\.tbl$", args.table):
        return dynamo.Table(args)
    else:
        print(f"unknown table format '{args.table}'", file=sys.stderr)


def get_output(avg, tbl, args):
    """Factory function which returns appropriate Output class"""
    average = get_average(avg)
    table = utils.Read_table(tbl)

    output_transformations = []
    for i in range(0, table.rows):
        transformation = get_table(table[i]).transformation
        output_transformations.append(transformation)

    with open("output.txt", "w") as f:
        for i in range(table.rows):
            line_to_write = str(i + 1) + "," \
                            + "".join(
                str(f"{e},").replace("[", "").replace("]", "").replace(" ", "") for e in output_transformations[i]) \
                            + "0,0,0,1\n"
            f.write(line_to_write)

        f.write("Mode:" + "\t" + str(average.mode) + "\n")
        f.write("Nc:" + "\t" + str(average.nc) + "\n")
        f.write("Nr:" + "\t" + str(average.nr) + "\n")
        f.write("Ns:" + "\t" + str(average.ns) + "\n")

        if args.compress:
            compress_flag = 1
            f.write(average.encoded_data_compressed)
        else:
            compress_flag = 0
            f.write(average.encoded_data)

    if not args.output:
        if compress_flag == 1:
            os.rename("output.txt", r"output_c.txt")
            print("Data is compressed.")
            print("output_c.txt is created.")
        elif compress_flag == 0:
            os.rename(rf"output.txt", r"output_nc.txt")
            print("Data is not compressed.")
            print("output_nc.txt is created.")
    elif args.output:
        os.rename(rf"output.txt", rf"{args.output}")
        if compress_flag == 0:
            print("Data is not compressed.")
        elif compress_flag == 1:
            print("Data is compressed.")
        print(f"{args.output}" + " is created.")


def main():
    args = parser.parse_args()
    # create the generic average object
    avg = get_average(args)
    # create the generic table object
    tbl = get_table(args)
    # create a generic output object
    out = get_output(avg, tbl, args)
    # write the output
    out.write()
    # output_txt(args)
    return sys.exit(0)  # constants which inform the OS on exit status


if __name__ == "__main__":
    sys.exit(main())
