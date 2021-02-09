"""
The script that runs the modules, and output the text file?
Also, it ignores calculation using data from tomograms
"""
import os
import sys

from new_main import TEST_DATA, parser
from new_main.average.brigg_map import Brigg_map as brigg_sta
from new_main.average.dynamo_em import EM as dynamo_sta
from new_main.table.brigg_motl import MotlRow as brigg_tbl
from new_main.table.dynamo_tbl import TblRow as dynamo_tbl
from new_main.table.read_table import Data

motl_data = os.path.join(TEST_DATA, 'motl', 'file.txt')

with open(motl_data) as _:
    print(_.read())


def output_txt(args):  # todo: change arguments into args
    data = Data(args.table)
    average = args.average
    output_transformations = []
    if average.endswith(".em"):  # Dynamo STA
        sta = dynamo_sta(average)
        for i in range(data.rows):
            row = dynamo_tbl(data[i]).transformation
            output_transformations.append(row.tolist())
        print("Data from Dynamo")
    if average.endswith(".map"):  # Brigg's STA format, or EMDB STA format
        sta = brigg_sta(average)
        for i in range(data.rows):
            row = brigg_tbl(data[i]).transformation
            output_transformations.append(row.tolist())
        print("Data from Brigg's lab")

    with open("output.txt", "w") as f:
        for i in range(data.rows):
            line_to_write = str(i + 1) + "," \
                            + "".join(
                str(f"{e},").replace("[", "").replace("]", "").replace(" ", "") for e in output_transformations[i]) \
                            + "0,0,0,1\n"
            f.write(line_to_write)

        f.write("Mode:" + "\t" + str(sta.mode) + "\n")
        f.write("Nc:" + "\t" + str(sta.nc) + "\n")
        f.write("Nr:" + "\t" + str(sta.nr) + "\n")
        f.write("Ns:" + "\t" + str(sta.ns) + "\n")

        if args.compress:
            compress_flag = 1
            if average.endswith(".em"):
                f.write(sta.encoded_data_compressed)
            if average.endswith(".map"):
                f.write(sta.encoded_data_compressed)
        else:
            compress_flag = 0
            if average.endswith(".em"):
                f.write(sta.encoded_data)
            if average.endswith(".map"):
                f.write(sta.encoded_data)

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
    output_txt(args)
    return sys.exit(0)  # constants which inform the OS on exit status


if __name__ == "__main__":
    sys.exit(main())
