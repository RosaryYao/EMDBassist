import struct, numpy, base64

class Encode_em:
    """ 
    Dynamo produces subtomogram averaging volume data in .em format and stores binary data.
    See EMDB_mapFormat MODE at http://ftp.ebi.ac.uk/pub/databases/emdb/doc/Map-format/current/EMDB_map_format.pdf,
    After unpacking, the first number indicates the type of data. It is then followed by 3 numbers, denoting the numbers of columns, rows and sections. 
    The rest is volume data. 
    Output file format:
        EMDB_mapFormat_mode
        nc
        nr
        ns
        volume_data
    """ 
    

    def __init__(self, filename):
        self.filename = filename

        with open(self.filename, 'rb') as em:
            # the header is 128 words = 512 bytes. np.dtype = "int32" (long integer)
            # we read the first 4 words (word = 4 bytes)
            self.dynamo_header = struct.unpack('128i', em.read(128*4))
            # determine the MODE
            self.dy_mode = int(hex(self.dynamo_header[0])[2])
            if self.dy_mode == 2: # int16, short int
                self.mode = 1
                type_flag = "h" 
            elif self.dy_mode == 4: # int32, int
                self.mode = 3
                type_flag = "i"
            elif self.dy_mode == 5: # float32
                self.mode = 2
                type_flag = "f"
            elif self.dy_mode == 9: # float64
                self.mode = 4
                type_flag = "d"
            else:
                raise Exception ("data not supported yet!")

            # pick the col, row, sect values
            self.nc, self.nr, self.ns = self.dynamo_header[1:4]
            # then we read the data
            # by default .read() reads from the current position to the end
            self.volume_encoded = base64.b64encode(em.read())
            em.seek(128*4)
            self.volume_data = struct.unpack(f'{self.nc * self.nr * self.ns}{type_flag}', em.read())
            
        #print(self.volume_encoded[:100])
        #print(type_flag)
        #print(self.volume_data[:10])

    ### Below create another method to output into a .txt file
    def output(self):
        output_text = input("Please name the output file: ")
        with open(f"{output_text}.txt", "w+") as f:
            f. write(str(self.nc) + "\n" + str(self.nr) +"\n" + str(self.ns) + "\n" + str(self.mode) + "\n" + str(self.volume_encoded)[2:]) # to remove b'
        print(f"{output_text}.txt" + " is created.")

    ### Below create another method to arrange the volume data into numpy.array()
    '''
    def array(self):
        import numpy
        voxel_array = numpy.array(self.volume_data).reshape(self.nc, self.nr, self.ns)
        return (voxel_array)
    '''

# a main function where you can call interactive stuff
def main():
    filename = input("Dynamo .em file: ")
    data = Encode_em(filename)
    data.output()
    #voxel_array = data.array()
    #print(voxel_array[:10])

main()