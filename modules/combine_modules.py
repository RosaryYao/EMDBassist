import transformation_dynamo as transform
import voxel_dynamo as voxel
import numpy
import os
"""
The output format:
-----------Transformation data--------------
(translation vector + "\t" + rotation matrix)*n
# Consider combining? 
-----------Map information-------------------
EMDB map format
nc
nr
ns
volume_data (in string)
"""

def combine_data(em, tbl, output):
    with open(tbl, "rt") as tbl:
        # Create a list that contains all the transformations, and each transformation is treated as an element in the list
        # As well as rotations
        translation_set = []
        rotation_set = []
        polygon = [1,1,1] # Just to make class Polygon works... Is there a better way? -> Rewrite the script? 

        for line in tbl:
            line = str(line).split(" ")
            vector = [float(line[3]), float(line[4]), float(line[5])]
            translation_set.append(vector)

            # rotation in zxz convension; rotation angle in the corresponding order: a, b, c.
            a, b, c = float(line[6]), float(line[7]), float(line[8]) 
            rotation = transform.Polygon(polygon).rotate(a=a, b=b, c=c)
            rotation_list = rotation.tolist()
            rotation_set.append(rotation_list)    

    # Output the final text file
    em = voxel.EM(em)
    with open(f"{output}.txt", "w+") as file:
        for i in range(len(rotation_set)):
            # fixme: write our values only with \t separation
            # fixme: add the index
            file.write(str(translation_set[i]) + "\t" + str(rotation_set[i]) + "\n")
        # fixme: bytes -> decode('utf-8')
        # fixme: add fieldname e.g. nc,nr,ns, data
        # todo: zip the data: https://docs.python.org/3/library/zlib.html
        file.write(str(em.mode) + "\n" + str(em.nc) + "\n" + str(em.nr) +"\n" + str(em.ns) + "\n" + str(em.volume_encoded)[2:])
    # strings are encoded; they have an encode method
    # encoding generates bytes
    # we encode using an encoding; most common is utf-8
    # byes are decoded; they have a decode method
    # decode using utf-8
    print(f"{output}.txt" + " is created.")

def main():
    # todo: consider using argparse library: https://docs.python.org/3/library/argparse.html
    # python my_script.py --em-file <path/file.em> --tbl-file <path/file.tbl>
    # python my_script.py <folder>
    # python my_script.py <prefix>
    em = input("Averaged particle file (.em): ")
    if not os.path.exists(em):
        raise ValueError(f"file '{em} does not exist")
    tbl = input("Transformation table (.tbl): ")
    output = input("Output file name (.txt)")
    combine_data(em,tbl,output)
main()




