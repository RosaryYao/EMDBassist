import math
import matplotlib.pyplot as plt
import matplotlib.patches as mp

tbl = open("random.txt","r")
tbl = list(tbl)
#print (tbl)
new_tbl = []
for each in tbl[1::]:
    each = (each.replace("\n",""))
    new_tbl.append(each.split("\t"))

A = [-3,5]
B = [4,2]
C = [6,-2]
D = [-5,-3]

# Extract centers and theta for each shape 
centers = []
theta = []
for i in range(len(new_tbl)):
    centers.append([int(new_tbl[i][1]),int(new_tbl[i][2])])
    theta.append(int(new_tbl[i][3]))
#print(centers[0:3])
#print(theta[0:3])

# Define the function "place()" to place the template to the desired positions
def place(A,B,C,D,P,theta):

    # 1. Clockwise rotation
    rotA = [A[0]*math.cos(theta)-A[1]*math.sin(theta), A[0]*math.sin(theta)+A[1]*math.cos(theta)]
    rotB = [B[0]*math.cos(theta)-B[1]*math.sin(theta), B[0]*math.sin(theta)+B[1]*math.cos(theta)]
    rotC = [C[0]*math.cos(theta)-C[1]*math.sin(theta), C[0]*math.sin(theta)+C[1]*math.cos(theta)]
    rotD = [D[0]*math.cos(theta)-D[1]*math.sin(theta), D[0]*math.sin(theta)+D[1]*math.cos(theta)]
    print(rotA,rotB,rotC,rotD)

    # 2. Translation 
    # translation = the vector needed to move the shape back to origin
    translation = [P[0],P[1]]

    # Call the 4 points after translation: Q,W,E,R
    Q = [rotA[0]+P[0],rotA[1]+P[1]]
    W = [rotB[0]+P[0],rotB[1]+P[1]]
    E = [rotC[0]+P[0],rotC[1]+P[1]]
    R = [rotD[0]+P[0],rotD[1]+P[1]]
    print(Q,W,E,R)
    
    return(Q,W,E,R)

# Create a list of placed shapes
placed = []
for i in range(len(new_tbl)):
    placed.append(place(A,B,C,D,centers[i],theta[i]))
#print(placed)

# Draw plots
# 1. Define polygons
pol_original = mp.Polygon((A,B,C,D),color="k")
fig,ax = plt.subplots()
ax.add_patch(pol_original)
for i in range(len(new_tbl)):
    polygon = mp.Polygon(placed[i],color="r",alpha=0.5)
    ax.add_patch(polygon)

# 2. Draw axes
ax.axhline(y=0,color="k",linestyle="--")
ax.axvline(x=0,color="k",linestyle="--")

# 3. Indicate centers
ax.scatter(0,0)
for each in centers:
    ax.scatter(each[0],each[1])

# 4. Show plots
plt.xlim(-30,30)
plt.ylim(-30,30)
plt.gca().set_aspect('equal',adjustable='box')
plt.show()


