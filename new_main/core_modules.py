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
        if args.verbose:
            print("Reading Briggs' subtomogram average (.map) and table (.em) files...")
        return average.motl.Average(args.average, args)
    elif re.match(r".*\.em$", args.average) and re.match(r".*\.tbl$", args.table):
        if args.verbose:
            print("Reading Dynamo subtomogram average (.em) and table (.tbl) files...")
        return average.dynamo.Average(args.average, args)

    # elif re.match(r".*\.rec$", args.average) and re.match(r".*\.mod$", args.table):
    #    return peet_a.Average(args.average)
    else:
        # todo: print(...)
        return None
        #raise TypeError(f"unknown average format '{args.average}'")


def get_table(args):
    """Factory function which returns appropriate Table class"""

    if re.match(r".*\.map$", args.average) and re.match(r".*\.em$", args.table):
        return table.motl.Table(args.table, args)
    elif re.match(r".*\.em$", args.average) and re.match(r".*\.tbl$", args.table):
        return table.dynamo.Table(args.table, args)
    # elif re.match(r".*\.rec$", args.average) and re.match(r".*\.mod$", args.table):
    #    return peet_t.Average(args.average)
    else:
        raise TypeError(f"unknown table format '{args.table}'")


def get_output(avg, tbl, args):
    """To be factory function which returns appropriate Output class"""
    with open(args.output, "w") as f:
        f.write("mode:" + "\t" + str(avg.mode) + "\n")
        f.write("nc:" + "\t" + str(avg.nc) + "\n")
        f.write("nr:" + "\t" + str(avg.nr) + "\n")
        f.write("ns:" + "\t" + str(avg.ns) + "\n")
        f.write(f"txs:\t{len(tbl)}\n")
        for i, each in enumerate(tbl):
            table_row = tbl[i]
            f.write(f"{i+1},{str(table_row)}")
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
