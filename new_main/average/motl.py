"""Output Briggs lab voxel data file, encoded in base64 as string"""

import mrcfile
import struct
import base64


class Brigg_map:
    def __init__(self, fn):
        self.fn = fn
        self.mode, self.cols, self.rows, self.sections, self.raw_data, self.origin, self.voxel_size = self._get_data(fn)
        self.encoded_data = self.encode_data()

    def _get_data(self, fn):
        with mrcfile.open(fn) as mrc:
            mode = mrc.header.mode
            cols = mrc.header.nx
            rows = mrc.header.ny
            sections = mrc.header.nz
            origin = mrc.header.nxstart, mrc.header.nystart, mrc.header.nzstart
            voxel_size = mrc.voxel_size  # Would be a tuple?
            data = mrc.data
        return mode, cols, rows, sections, data, origin, voxel_size

    def encode_data(self):
        if self.mode == 2:
            type_flag = "f"
        elif self.mode == 1:
            type_flag = "h"
        elif self.mode == 3:
            type_flag = "i"
        elif self.mode == 4:
            type_flag = "d"
        else:
            raise TypeError("The map mode is not supported yet!")

        raw_data = self.raw_data.flatten()
        packed_data = struct.pack(f"{self.cols * self.rows * self.sections}{type_flag}", *raw_data)
        encoded_data = base64.b64encode(packed_data).decode("utf-8")
        return encoded_data

    @property
    def encoded_data_compressed(self):
        import zlib
        compressed_raw_data = zlib.compress(self.raw_data.flatten())
        return base64.b64encode(compressed_raw_data).decode("utf-8")


class Average:
    def __init__(self, args):
        self._args = args

#map = Brigg_map("emd_3465.map")
#print(map.encoded_data[0:10])
#print(map.encoded_data_compressed[0:10])


