import argparse
import base64
import struct
import re

import numpy
import mrcfile
from masks import cli, main


args = cli.cli(f"masks make -I 160 -M 60 -P 50 -D 3 -s ellipse")
mask = main.make_mask(args).mask
# print(mask[80][80][40:120])
# print(mask[40][40][40:120])
# print(mask[39][40][40:120])
mask_np = numpy.asarray(mask)
print(type(mask_np))
print(mask_np.shape)

map = mrcfile.open("emd_3465.map")
raw_data = map.data
raw_data_np = numpy.asarray(raw_data)

mask_map = numpy.multiply(raw_data_np, numpy.array(mask_np))
# print(mask_map.shape)
# print(mask_map[80][80][40:80])

data_flatten = mask_map.flatten()

packed_data = struct.pack(f"{len(data_flatten)}f", *data_flatten)
encoded_data = base64.b64encode(packed_data)
decoded_data = encoded_data.decode('utf-8')
# print(decoded_data[1030440])

with open("motl_1_full.txt", "r") as input:
    rows = input.readlines()
    not_data = re.compile(r"^Data")
    with open("masked_motl_1.txt", "w") as output:
        for each in rows:
            if not not_data.match(each):
                output.write(each)
        output.write(f"Data:\t{decoded_data}")
        print("output saved!")





# todo: complete arg_parse()
"""
def arg_parse():
    parser = argparse.ArgumentParser(description="Mask a .map or .mrc file")
    parser.add_argument("-o", "--output", help="the output file name (.txt)")
    parser.add_argument("-M", "--map_file", help="The EMDB map file")
    parser.add_argument('-I', '--image-size', nargs='+', default=(10,), type=int, help='image size [10,10]')
"""

