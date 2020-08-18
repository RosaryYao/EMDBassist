import math
import sys
import matplotlib.pyplot as plt

# f = open("random_3d.txt", "r")
# print(type(tbl))
# tbl = list(tbl)
# print(type(tbl))
# print (tbl)
# new_tbl = []
# for each in tbl[1::]:
#     each = (each.replace("\n", ""))
#     new_tbl.append(each.split("\t"))

new_tbl = list()
with open("random_3d.txt", 'r') as f: # context manager
    for row in f: # iterate over the file (file is iterable)
        l = row.strip().split('\t')
        if l[0] == 'id':
            continue # go to the next iteration
        new_tbl.append(l)



# sys.exit(0)

A = [1, 2, 3]
B = [-1, 2, 3]
C = [-1, -2, -3]
D = [1, -2, -3]

# If a polygon is meant to be drawn:
xo = [1, -1, -1, 1]
yo = [2, 2, -2, -2]
zo = [3, 3, -3, -3]

# Extract centers and theta for each shape 
centers = []
theta = []
for i in range(len(new_tbl)):
    centers.append([int(new_tbl[i][1]), int(new_tbl[i][2]), int(new_tbl[i][3])])
    theta.append([int(new_tbl[i][4]), int(new_tbl[i][5]), int(new_tbl[i][6])])


# print(centers[0:3])
# print(theta[0:3])

# Define the function "place()" to place the template to the desired positions
def place(A, B, C, D, centers, theta):
    theta_x = theta[0]
    theta_y = theta[1]
    theta_z = theta[2]

    # 1. Clockwise rotation
    # todo: please help me understand the choice of clockwise; it might explain the comments below
    # todo: the convention is that positive angles imply *counterclockwise* rotations
    # 1.1 rotation about x-axis => theta_x
    # please correct me if I'm wrong
    # fixme: I don't think the second component of rot*x is correct (should it be A[1]*cos(theta_x) - A[2]*sin(theta_x)?)
    rotAx = [A[0],A[1]*math.cos(theta_x)+A[2]*math.sin(theta_x), -A[1]*math.sin(theta_x)+A[2]*math.cos(theta_x)]
    rotBx = [B[0],B[1]*math.cos(theta_x)+B[2]*math.sin(theta_x), -B[1]*math.sin(theta_x)+B[2]*math.cos(theta_x)]
    rotCx = [C[0],C[1]*math.cos(theta_x)+C[2]*math.sin(theta_x), -C[1]*math.sin(theta_x)+C[2]*math.cos(theta_x)]
    rotDx = [D[0],D[1]*math.cos(theta_x)+D[2]*math.sin(theta_x), -D[1]*math.sin(theta_x)+D[2]*math.cos(theta_x)]
    #print(rotAx,rotBx,rotCx,rotDx)

    # todo: consider using matrix algebra for the computations
    #   this way it will be easier to avoid bugs
    # 1. install numpy
    # I've created virtual env in the main folder called EMDBassist.env
    # This will allow you to create a virtual environment to work in which is reproducible.
    # Once you have create and activated the virtual env run:
    #   pip install -r EMDBassist.env
    # 2. Create a 'matrix' using numpy
    #   import numpy
    #   import math
    #   # for example the x rotation matrix by 40 degrees would be:
    #   matrix = numpy.array([
    #       [1, 0, 0],
    #       [0, math.cos(40), -math.sin(40)],
    #       [0, math.sin(40),  math.cos(40)]
    #   ])
    # 3. Multipy a point (x, y, z) = [5, 12, 33] using the dot product
    #   point = numpy.array([[5], [12], [33]]) # note: a column vector
    #   rotated_point = matrix.dot(point)
    #
    # To make a generic rotation consider a rotate_x(theta) function
    #   def rotate_x(theta):
    #       return numpy.array([
    #           [1, 0, 0],
    #           [0, math.cos(theta), -math.sin(theta)],
    #           [0, math.sin(theta),  math.cos(theta)],
    #       ])
    # which you can use for an arbitrary theta
    #   rotated_point = rotate_x(37).dot(point)
    # You can do the same with rotate_y and rotate_z


    # 1.2 rotation about y-axis => theta_y
    # fixme: I don't think the first component of rot*y is correct (should it be rotAx[0]*cos(theta_y) + rotAx[2]*sin(theta_y)?)
    # fixme: I don't think the third component of rot*y is correct (should it be -rotAx[0]*sin(theta_y) + rotAx[2]*cos(theta_y)?)
    rotAy = [rotAx[0] * math.cos(theta_y) - rotAx[2] * math.sin(theta_y), rotAx[1],
             rotAx[0] * math.sin(theta_y) + rotAx[2] * math.cos(theta_y)]
    rotBy = [rotBx[0] * math.cos(theta_y) - rotBx[2] * math.sin(theta_y), rotBx[1],
             rotBx[0] * math.sin(theta_y) + rotBx[2] * math.cos(theta_y)]
    rotCy = [rotCx[0] * math.cos(theta_y) - rotCx[2] * math.sin(theta_y), rotCx[1],
             rotCx[0] * math.sin(theta_y) + rotCx[2] * math.cos(theta_y)]
    rotDy = [rotDx[0] * math.cos(theta_y) - rotDx[2] * math.sin(theta_y), rotDx[1],
             rotDx[0] * math.sin(theta_y) + rotDx[2] * math.cos(theta_y)]

    # 1.3 rotation about z-axis =>  theta_z
    # fixme: I don't think the first component of rot*z is correct (should it be rotAy[0]*cos(theta_z) - rotAy[1]*sin(theta_z)?)
    # fixme: I don't think the second component of rot*z is correct (should it be rotAy[0]*sin(theta_z) + rotAy[1]*cos(theta_z)?)
    rotAz = [rotAy[0] * math.cos(theta_z) + rotAy[1] * math.sin(theta_z),
             -rotAy[0] * math.sin(theta_z) + rotAy[1] * math.cos(theta_z), rotAy[2]]
    rotBz = [rotBy[0] * math.cos(theta_z) + rotBy[1] * math.sin(theta_z),
             -rotBy[0] * math.sin(theta_z) + rotBy[1] * math.cos(theta_z), rotBy[2]]
    rotCz = [rotCy[0] * math.cos(theta_z) + rotCy[1] * math.sin(theta_z),
             -rotCy[0] * math.sin(theta_z) + rotCy[1] * math.cos(theta_z), rotCy[2]]
    rotDz = [rotDy[0] * math.cos(theta_z) + rotDy[1] * math.sin(theta_z),
             -rotDy[0] * math.sin(theta_z) + rotDy[1] * math.cos(theta_z), rotDy[2]]

    # 2. Translation 

    # Call the 4 points after translation: Q,W,E,R
    Q = [rotAz[0] + centers[0], rotAz[1] + centers[1], rotAz[2] + centers[2]]
    W = [rotBz[0] + centers[0], rotBz[1] + centers[1], rotBz[2] + centers[2]]
    E = [rotCz[0] + centers[0], rotCz[1] + centers[1], rotCz[2] + centers[2]]
    R = [rotDz[0] + centers[0], rotDz[1] + centers[1], rotDz[2] + centers[2]]
    # print(Q,W,E,R)

    return (Q, W, E, R)


# Create a list of placed shapes
placed = []
for i in range(len(new_tbl)):
    placed.append(place(A, B, C, D, centers[i], theta[i]))
print(placed[0:3])

# Plotting
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
# 1. Arrange the points into array
x, y, z = [], [], []

for each in range(len(placed)):
    for i in placed[each]:
        x.append(i[0])
        y.append(i[1])
        z.append(i[2])
    ax.plot_trisurf(x, y, z, color="r", alpha=0.5)
    x, y, z = [], [], []
print(x, y, z)

# plot the template 
ax.plot_trisurf(xo, yo, zo, color="k")

ax.set_xlim3d([-30, 30])
ax.set_ylim3d([-30, 30])
ax.set_zlim3d([-30, 30])

plt.show()
