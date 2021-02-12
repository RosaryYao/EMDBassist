import mrcfile
import struct
import base64


class Average:
    """
    Dynamo produces subtomogram averaging volume data in .em format and stores binary data.
    See EMDB_mapFormat MODE at http://ftp.ebi.ac.uk/pub/databases/emdb/doc/Map-format/current/EMDB_map_format.pdf,
    After unpacking, the first number indicates the type of data. It is then followed by 3 numbers, denoting the numbers of columns, rows and sections.
    The rest is volume data.
    """

    def __init__(self, filename):
        self.filename = filename

        with open(self.filename, 'rb') as em:
            # the header is 128 words = 512 bytes. np.dtype = "int32" (long integer)
            # we read the first 4 words (word = 4 bytes)
            self.dynamo_header = struct.unpack('128i', em.read(128 * 4))
            # determine the MODE
            self.dy_mode = int(hex(self.dynamo_header[0])[2])
            if self.dy_mode == 2:  # int16, short int
                self.mode = 1
                type_flag = "h"
            elif self.dy_mode == 4:  # int32, int
                self.mode = 3
                type_flag = "i"
            elif self.dy_mode == 5:  # float32
                self.mode = 2
                type_flag = "f"
            elif self.dy_mode == 9:  # float64
                self.mode = 4
                type_flag = "d"
            else:
                raise NotImplementedError("data not supported yet!")

            # pick the col, row, sect values
            self.nc, self.nr, self.ns = self.dynamo_header[1:4]
            # then we read the data
            self.raw_data = em.read()
            self.volume_data = struct.unpack(f'{self.nc * self.nr * self.ns}{type_flag}', self.raw_data)
            # self.encoded_data = base64.b64encode(self.volume_data).decode("utf-8")
            self.encoded_data = base64.b64encode(self.raw_data).decode("utf-8")

    @property
    def encoded_data_compressed(self):
        import zlib
        compressed_raw_data = zlib.compress(self.raw_data)
        return base64.b64encode(compressed_raw_data).decode("utf-8")
