import random
import math

tbl = open("random.txt","w+")
tbl.write("id"+"\t"+"center_x"+"\t"+"center_y"+"\t"+"theta"+"\n")
for i in range(1,21):
    x = random.randint(-25,25)
    y = random.randint(-25,25)
    theta = random.randint(-360,360)
    tbl.write(str(i)+"\t")
    tbl.write(str(x)+"\t")
    tbl.write(str(y)+"\t")
    tbl.write(str(theta)+"\n")
tbl.close()
