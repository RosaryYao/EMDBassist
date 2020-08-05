import matplotlib
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111,projection="3d")
# matplotlib 把一列，作为一个点。如下：

x = [1,-1,-1,1]
y = [2,2,-2,-2]
z = [3,3,-3,-3]

ax.plot_trisurf(x,y,z)
ax.scatter(x,y,z)

ax.set_xlim3d([-5,5])
ax.set_ylim3d([-5,5])
ax.set_zlim3d([-10,10])

# Would be best, if could show the x,y,z axes...

plt.show()

# LIST THE ROTATION MATRICES
# Anticlockwise:
# rotation along x-axis: [(1,0,0),(0,cosa,sina),(0,-sina,cosa)]
# rotation along y-axis: [(cosa,0,-sina),(0,1,0),(sina,0,cosa)]
# rotation along z-axis: [(cosa,sina,0),(-sina,cosa,0),(0,0,1)]
# Clockwise:
# rotation along x-axis: change theta into -theta