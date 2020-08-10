import random

tbl = open("random_3d.txt","w+")
tbl.write("id"+"\t"+"center_x"+"\t"+"center_y"+"\t"+"center_z"+"\t"+"theta_x"+"\t"+"theta_y"+"\t"+"theta_z"+"\n")
for i in range(1,21):
    x = random.randint(-25,25)
    y = random.randint(-25,25)
    z = random.randint(-25,25)
    theta_x = random.randint(-360,360)
    theta_y = random.randint(-360,360)
    theta_z = random.randint(-360,360)
    tbl.write(str(i)+"\t")
    tbl.write(str(x)+"\t")
    tbl.write(str(y)+"\t")
    tbl.write(str(z)+"\t")
    tbl.write(str(theta_x)+"\t"+str(theta_y)+"\t")
    tbl.write(str(theta_z)+"\n")
tbl.close()
