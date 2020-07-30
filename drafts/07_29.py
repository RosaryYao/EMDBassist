import matplotlib.pyplot as plt
import matplotlib.patches as mp
import math
import random
import sympy

# Define "template"
O = [0,0]
A = [random.randrange(-5,0,1), random.randrange(0,5,1)]
B = [random.randrange(0,5,1), random.randrange(0,5,1)]
C = [random.randrange(0,5,1), random.randrange(-5,0,1)]
D = [random.randrange(-5,0,1), random.randrange(-5,0,1)]

points = [A,B,C,D]
#print(points)
polygon = mp.Polygon((points), closed = True,fill=None,edgecolor="r", alpha=0.9)

# Random transformation
# 1. Rotation
theta = random.randrange(-360,360)
print('randomly generated theta is: ', theta) #theta is clockwise rotation
theta = math.radians(theta)
rotA = [A[0]*math.cos(theta)+A[1]*math.sin(theta), -A[0]*math.sin(theta)+A[1]*math.cos(theta)]
rotB = [B[0]*math.cos(theta)+B[1]*math.sin(theta), -B[0]*math.sin(theta)+B[1]*math.cos(theta)]
rotC = [C[0]*math.cos(theta)+C[1]*math.sin(theta), -C[0]*math.sin(theta)+C[1]*math.cos(theta)]
rotD = [D[0]*math.cos(theta)+D[1]*math.sin(theta), -D[0]*math.sin(theta)+D[1]*math.cos(theta)]
rotpoints = [rotA,rotB,rotC,rotD]
rotpolygon = mp.Polygon((rotpoints),closed=True,fill=None,edgecolor="b",alpha = 0.4)
#print(rotpoints)

# 2. Translation
P = [random.randrange(10,20,1),random.randrange(-5,-20,-1)]
traA,traB,traC,traD = [],[],[],[]
for i in [0,1]:
    traA.append(P[i]+rotA[i])
    traB.append(P[i]+rotB[i])
    traC.append(P[i]+rotC[i])
    traD.append(P[i]+rotD[i])
translated = [traA,traB,traC,traD]
trapolygon = mp.Polygon((translated),closed=True,fill=None,edgecolor="g",alpha=0.4)
#print(translated)

# As theta and translation are randomly generated; 
# Next: solve for theta and translation

# 1. Translation (would be easier and more straight away?)
# translation = the vector needed to move the shape back to origin
translation = [-P[0],-P[1]]
# Call the 4 points after "inverse" translation Q,W,E,R => Just to visualize the transformation
Q,W,E,R = [],[],[],[]
for i in [0,1]:
    Q.append(traA[i]+translation[i])
    W.append(traB[i]+translation[i])
    E.append(traC[i]+translation[i])
    R.append(traD[i]+translation[i])
translation_points = [Q,W,E,R]
print("Translation is: ", translation)
#print("the type of Q:", type(Q))
#print(translation_points)
polygon_translated = mp.Polygon((translation_points),closed = True, fill=True,alpha=0.4)


# 2. Rotation
# coordinates A,B,C,D and Q,W,E,R known
# Needs to be done on only one "complementary" coordinates - A and Q are "complementary" coordinates
a,b,c,d = A[0],A[1],Q[0],Q[1]
#print(a,b,c,d)

x = sympy.Symbol('x')
y = sympy.Symbol('y')
# cos(phi) = x, sin(phi) = y
#print(sympy.solve([a*x+b*y-c,b*x-a*y-d],[x,y])) 
#print(type(solve([a*x+b*y-c,b*x-a*y-d],[x,y])))
solution = sympy.solve([a*x+b*y-c,b*x-a*y-d],[x,y])
x = solution[x]
#print(x)
phi = math.acos(x)
print("the anticlockwise rotation in degree should be: ", math.degrees(phi))

# Define the points after rotation, from Q,W,E,R into rot(Q,W,E,R)
rotQ = [Q[0]*math.cos(phi)-Q[1]*math.sin(phi), Q[0]*math.sin(phi)+Q[1]*math.cos(phi)]
rotW = [W[0]*math.cos(phi)-W[1]*math.sin(phi), W[0]*math.sin(phi)+W[1]*math.cos(phi)]
rotE = [E[0]*math.cos(phi)-E[1]*math.sin(phi), E[0]*math.sin(phi)+E[1]*math.cos(phi)]
rotR = [R[0]*math.cos(phi)-R[1]*math.sin(phi), R[0]*math.sin(phi)+R[1]*math.cos(phi)]

rotation_points = [rotQ,rotW,rotE,rotR]
polygon_rotated = mp.Polygon((rotation_points),closed = True,fill = True, color = "y", alpha=0.4)
print("randomly generated coordiantes: ",A,B,C,D)
print("resolved coordiantes: ", rotation_points)


# Draw plot
fig,ax=plt.subplots()
ax.add_patch(polygon)
ax.add_patch(rotpolygon)
ax.add_patch(trapolygon)
ax.add_patch(polygon_translated)
ax.add_patch(polygon_rotated)
ax.axhline(y=0,color="k",linestyle="--")
ax.axvline(x=0,color="k",linestyle="--")
ax.scatter(P[0],P[1])
ax.scatter(0,0)
plt.xlim(-30,30)
plt.ylim(-30,30)
plt.gca().set_aspect('equal',adjustable='box')
plt.show()
