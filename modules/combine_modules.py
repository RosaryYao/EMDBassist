import transformation_dynamo as transform
import voxel_dynamo as voxel
import numpy 

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
            file.write(str(translation_set[i]) + "\t" + str(rotation_set[i]) + "\n")
        file.write(str(em.mode) + "\n" + str(em.nc) + "\n" + str(em.nr) +"\n" + str(em.ns) + "\n" + str(em.volume_encoded)[2:])
    
    print(f"{output}.txt" + " is created.")

def main():
    em = input("Averaged particle file (.em): ")
    tbl = input("Transformation table (.tbl): ")
    output = input("Output file name (.txt)")
    combine_data(em,tbl,output)
main()




