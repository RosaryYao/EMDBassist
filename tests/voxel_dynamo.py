import struct, numpy

class Encode_em:
    """ 
    Dynamo produces subtomogram averaging volume data in .em format and stores binary data.
    According to EMDB_mapFormat, http://ftp.ebi.ac.uk/pub/databases/emdb/doc/Map-format/current/EMDB_map_format.pdf,
    the mode is 1 for .em format, so density is stored as a signed integer (range -32768 to 32767, ISO/IEC 10967).
    After unpacking, the first number is "83886086", followed by 3 numbers, denoting the numbers of columns, rows and sections. 
    The rest is volume data. 
    Output file format:
        nc
        nr
        ns
        EMDB_mapFormat_mode
        volume_data
    """ 
    

    def __init__(self):
        filename = input("Dynamo .em file: ")
        with open(filename, "rb") as em:
            voxel = em.read()
        length = int(len(voxel)/4)
        data = struct.unpack(f"{length}i", voxel)
        self.dynamo_header = data[0]

        # number of columns, rows, sections:
        self.nc, self.nr, self.ns = data[1], data[2], data[3]
        flag = int(length - (self.nc)*(self.nr)*(self.ns))
        self.volume_data = data[flag:] # Otherwise there would be a lot of 0s, and cannot be reshaped into numpy.array() of shape (nc, nr, ns)

    ### Below create another method to output into a .txt file
    def output(self):
        output_text = input("Please name the output file: ")
        with open(f"{output_text}.txt", "w+") as f:
            f. write(str(self.nc) + "\n" + str(self.nr) +"\n" + str(self.ns) + "\n" + "1" + "\n" + str(self.volume_data))
        print(f"{output_text}.txt" + " is created.")

    ### Below create another method to arrange the volume data into numpy.array()
    def array(self):
        import numpy
        voxel_array = numpy.array(self.volume_data).reshape(self.nc, self.nr, self.ns)
        return (voxel_array)

data = Encode_em()
#data.output()
voxel_array = data.array()
print(voxel_array[:10])