"""
The script that runs the modules, and output the text file?
Also, it ignores calculation using data from tomograms
"""
import os
import re
import sys
import platform

from . import parser, average, table


def get_average(args):
    """Factory function which returns appropriate Average class"""
    if re.match(r".*\.map$", args.average) and re.match(r".*\.em$", args.table):
        return average.motl.Average(args.average, args)
    elif re.match(r".*\.em$", args.average) and re.match(r".*\.tbl$", args.table):
        return average.dynamo.Average(args.average, args)
        # todo: change the interface, takes args in addition for modification
    # elif re.match(r".*\.rec$", args.average) and re.match(r".*\.mod$", args.table):
    #    return peet_a.Average(args.average)
    else:
        print(f"unknown average format '{args.average}'", file=sys.stderr)


def get_table(args):
    """Factory function which returns appropriate Table class"""

    if re.match(r".*\.map$", args.average) and re.match(r".*\.em$", args.table):
        return table.motl.Table(args.table, args)
    elif re.match(r".*\.em$", args.average) and re.match(r".*\.tbl$", args.table):
        return table.dynamo.Table(args.table, args)  # todo: fix dynamo_t as well
    # elif re.match(r".*\.rec$", args.average) and re.match(r".*\.mod$", args.table):
    #    return peet_t.Average(args.average)
    else:
        print(f"unknown table format '{args.table}'", file=sys.stderr)


def get_output(avg, tbl, args):
    """To be factory function which returns appropriate Output class"""
    with open(args.output, "w") as f:
        # fixme: once a class has a __iter__() method we simply iterate over the class
        for i, each in enumerate(tbl.__iter__()):
            # fixme: once a class has a __getitem__() method we simply use [i] syntax
            table_row = tbl.__getitem__(i)
            f.write(f"{i+1},")
            # fixme: once a class has a __str__() method just use str(obj) to stringify it
            f.write(table_row.__str__())

        f.write("Mode:" + "\t" + str(avg.mode) + "\n")
        f.write("Nc:" + "\t" + str(avg.nc) + "\n")
        f.write("Nr:" + "\t" + str(avg.nr) + "\n")
        f.write("Ns:" + "\t" + str(avg.ns) + "\n")

        if args.compress:
            f.write(avg.encoded_data_compressed)
            print(f"{args.output} is created, volume data is compressed.")
        else:
            f.write(avg.encoded_data)
            print(f"{args.output} is created, volume data is not compressed.")


def main():
    args = parser.parse_args()
    if args is None:
        if platform.system() == "Windows":
            return 64
        return os.EX_USAGE
    # create the generic average object
    avg = get_average(args)
    # create the generic table object
    tbl = get_table(args)
    get_output(avg, tbl, args)
    if platform.system() == "Windows":
        return sys.exit(0)
    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
