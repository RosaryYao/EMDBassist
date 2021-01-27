"""
The script that runs the modules, and output the text file?
Also, it ignores calculation using data from tomograms
"""
import os

from average.dynamo_em import EM as dynamo_sta
from table.dynamo_tbl import TblRow as dynamo_tbl
from average.brigg_map import Brigg_map as brigg_sta
from table.brigg_motl import MotlRow as brigg_tbl
from table.read_table import Data


def output_txt(average, table, compress=0, output=False):
    data = Data(table)
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

        if compress == 1:
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

    if not output:
        if compress_flag == 1:
            os.rename("output.txt", r"output_c.txt")
            print("Data is compressed.")
            print("output_c.txt is created.")
        elif compress_flag == 0:
            os.rename(rf"output.txt", r"output_nc.txt")
            print("Data is not compressed.")
            print("output_nc.txt is created.")
    elif output:
        os.rename(rf"output.txt", rf"{output}")
        if compress_flag == 0:
            print("Data is not compressed.")
        elif compress_flag == 1:
            print("Data is compressed.")
        print(f"{output}" + " is created.")


average = "emd_1305_averaged.em"
table = "emd_1305_averaged.tbl"
output_txt(average, table)











