import math

import matplotlib.pyplot as plt
import numpy as np

a = (3, 5, 1)
vector = (1, 2, 3)


class Point:
    """
    Transform a point, in right-hand system. A positive rotation == clockwise rotation
    Has attributes rotate_x, rotate_y, rotate_z, translate
    """

    def __init__(self, point, theta=0):
        self.point = np.array([[point[0]], [point[1]], [point[2]]])
        self.theta = theta
        self.empty = [0, 0, 0]

    def rotate_x(self, theta):
        matrix_x = np.array([
            [1, 0, 0],
            [0, math.cos(theta), math.sin(theta)],
            [0, -math.sin(theta), math.cos(theta)]
        ])

        product = np.dot(matrix_x, self.point)
        for i in range(3):
            self.empty[i] = float(product[i])

        return tuple(self.empty)

    def rotate_y(self, theta):
        matrix_y = np.array([
            [math.cos(theta), 0, -math.sin(theta)],
            [0, 1, 0],
            [math.sin(theta), 0, math.cos(theta)]
        ])

        product = np.dot(matrix_y, self.point)
        for i in range(3):
            self.empty[i] = float(product[i])

        return tuple(self.empty)

    def rotate_z(self, theta):
        matrix_z = np.array([
            [math.cos(theta), math.sin(theta), 0],
            [-math.sin(theta), math.cos(theta), 0],
            [0, 0, 1]
        ])

        product = np.dot(matrix_z, self.point)
        for i in range(3):
            self.empty[i] = float(product[i])

        return tuple(self.empty)

    def translate(self, vector):
        # vector = distance matrix, also in the form of a tuple
        for i in range(3):
            self.empty[i] = float((self.point[i] + vector[i]))
        return tuple(self.empty)


class Polygon:
    """
    This class has attributes plot_polygon, translate_polygon, and rotate_polygon.
    Note: if rotation + translation would like to be done on a given polygon, must do rotation first.  
    """

    def __init__(self, polygon):
        self.points = polygon
        self.points_as_matrix = np.array(polygon).T

        # To avoid following repetitions when rotation or translation involves
        # To use the attributes of the class "Point"
        self.point_set = []
        for each in self.points:
            self.point_set.append(Point(each))

    def x_rotation_matrix(self, theta):
        return np.array([
            [1, 0, 0],
            [0, math.cos(theta), -math.sin(theta)],
            [0, math.sin(theta), math.cos(theta)],
        ])

    def rotate_x(self, theta):
        return Polygon(self.x_rotation_matrix(theta).dot(self.points_as_matrix).T.tolist())

    def plot_polygon(self):
        x, y, z = [], [], []
        for each in self.points:
            x.append(each[0])
            y.append(each[1])
            z.append(each[2])
        # Plotting
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.plot_trisurf(x, y, z, color="k")

        ax.set_xlim3d([-10, 10])
        ax.set_ylim3d([-10, 10])
        ax.set_zlim3d([-10, 10])

        plt.show()

    def __str__(self):
        return f"Polygon({self.points})"

    def transform_polygon(self, axis="x", theta=0, vector=[0, 0, 0]):
        # Combine two methods (rotation and translation) - as rotation must be done before translation
        # If not specified, theta = 0, and vector = [0,0,0]

        # ROTATION
        rotated_points = []
        if axis == "x":
            for each in self.point_set:
                rotated_points.append(each.rotate_x(theta))
        elif axis == "y":
            for each in self.point_set:
                rotated_points.append(each.rotate_y(theta))
        elif axis == "z":
            for each in self.point_set:
                rotated_points.append(each.rotate_z(theta))

        # TRANSLATION
        rotated_points_Point = []
        for each in rotated_points:
            rotated_points_Point.append(Point(each))

        transformed_points = []
        for each in rotated_points_Point:
            transformed_points.append(each.translate(vector))

        return transformed_points


"""-----------------------------------------------------------
# Test 1: point.rotate()
theta = math.radians(45)
point = [1,2,3]
rotAx = [point[0], point[1]*math.cos(theta)+point[2]*math.sin(theta), -point[1]*math.sin(theta)+point[2]*math.cos(theta)]
print("*",rotAx)
point = Point(point)
print("*", point.rotate_x(theta))
---------------------------------------------------------------"""

"""----------------------------------------------------------------
# Test 2: polygon.transform_polygon()
theta = math.radians(45)
polygon = (
    (1, 1, 1),
    (1, 2, 3),
    (-1, 2, 3),
    (-1, -2, 3)
)

a = Polygon(polygon)
a.plot_polygon()

b = a.transform_polygon(vector=[1,1,1])
b = Polygon(b)
b.plot_polygon()

c = a.transform_polygon("y",theta=theta)
c = Polygon(c)
c.plot_polygon()

d = a.transform_polygon(theta = theta, vector = [2,2,2])
d = Polygon(d)
d.plot_polygon()
----------------------------------------------------------------"""

# To combine the plots into one graph? 
# polygon = (
#     (1, 1, 1),
#     (1, 2, 3),
#     (-1, 2, 3),
#     (-1, -2, 3)
# )
polygon  = (
    (1, 1, 0),
    (2, 1, 0),
    (2, 0, 0),
    (1, 0, 0)
)
# rotated to
# (-1, 1, 0), (-1, 2, 0), (0, 2, 0), (0, 1, 0)

a = Polygon(polygon)
print(a)
print(a.points_as_matrix)
rotated_polygon = a.rotate_x(math.radians(90))
print(rotated_polygon)
a.plot_polygon()

