# Transformation in 2D

import matplotlib.pyplot as plt
import matplotlib.patches as mp
import math
import random
import sympy

def generate_at_origin():
    # Randomly generate 4 edges, with center on (0,0)
    O = [0,0]
    A = [random.randrange(-5,0,1), random.randrange(0,5,1)]
    B = [random.randrange(0,5,1), random.randrange(0,5,1)]
    C = [random.randrange(0,5,1), random.randrange(-5,0,1)]
    D = [random.randrange(-5,0,1), random.randrange(-5,0,1)]
    points = [A,B,C,D]
    # Draw the polygon
    #polygon = mp.Polygon((points), closed = True,fill=None,edgecolor="r", alpha=0.5)
    #fig,ax=plt.subplots()
    #ax.add_patch(polygon)
    #ax.axhline(y=0,color="k",linestyle="--")
    #ax.axvline(x=0,color="k",linestyle="--")
    #ax.scatter(0,0)
    #plt.xlim(-8,8)
    #plt.ylim(-8,8)
    #plt.gca().set_aspect('equal',adjustable='box')
    #plt.show()
    print("randomly generated coordiantes: ",A,B,C,D)
    return(A,B,C,D)

def transformation(A,B,C,D):
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
    P = [random.randrange(10,25,1),random.randrange(-5,-25,-1)]
    traA,traB,traC,traD = [],[],[],[]
    for i in [0,1]:
        traA.append(P[i]+rotA[i])
        traB.append(P[i]+rotB[i])
        traC.append(P[i]+rotC[i])
        traD.append(P[i]+rotD[i])
    translated = [traA,traB,traC,traD]
    print("randomly generated center: ",P)
    
    # Draw the polygon
    #trapolygon = mp.Polygon((translated),closed=True,fill=None,edgecolor="g")
    #fig,ax=plt.subplots()
    #ax.add_patch(trapolygon)
    #ax.axhline(y=0,color="k",linestyle="--")
    #ax.axvline(x=0,color="k",linestyle="--")
    #ax.scatter(0,0)
    #plt.xlim(-30,30)
    #plt.ylim(-30,30)
    #plt.gca().set_aspect('equal',adjustable='box')
    #plt.show()
    return([traA,traB,traC,traD,P])

def resolve(A,B,C,D,traA,traB,traC,traD,P):
    import sympy
    # 1. Translation (would be easier and more straight away?)
    # translation = the vector needed to move the shape back to origin
    translationA = [-P[0],-P[1]]

    # Call the 4 points after "inverse" translation Q,W,E,R
    Q,W,E,R = [],[],[],[]
    for i in [0,1]:
        Q.append(traA[i]+translationA[i])
        W.append(traB[i]+translationA[i])
        E.append(traC[i]+translationA[i])
        R.append(traD[i]+translationA[i])
    translation_points = [Q,W,E,R]
    print("Translation is: ", translationA)


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
    print("resolved coordiantes: ", rotation_points)
    return(rotation_points)

A,B,C,D = generate_at_origin()
I,J,K,L,P = transformation(A,B,C,D)
#Q,W,E,R,P = transformation(A,B,C,D)

resolved_one = resolve(A,B,C,D,I,J,K,L,P)
#resolved_two = resolve(A,B,C,D,Q,W,E,R,P)

pol_original = mp.Polygon((A,B,C,D),color="g")
pol1 = mp.Polygon((I,J,K,L),color="b")
#pol2 = mp.Polygon((Q,W,E,R),color="y")
pol3 = mp.Polygon((resolved_one),color='r',alpha=0.5)
#pol4 = mp.Polygon((resolved_two),color='k',alpha=0.5)
fig,ax = plt.subplots()
ax.add_patch(pol_original)
ax.add_patch(pol1)
#ax.add_patch(pol2)
ax.add_patch(pol3)
#ax.add_patch(pol4)
ax.axhline(y=0,color="k",linestyle="--")
ax.axvline(x=0,color="k",linestyle="--")
ax.scatter(0,0)
plt.xlim(-30,30)
plt.ylim(-30,30)
plt.gca().set_aspect('equal',adjustable='box')
plt.show()
