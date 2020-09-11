import math
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import numpy as np

class Point:
    """
    Transform a point, in right-hand system. A positive rotation == clockwise rotation
    Has attributes rotate_x, rotate_y, rotate_z, translate
    """
    def __init__(self, point, theta=0, vector=(0,0,0)):
        self.point = np.array([[point[0]],[point[1]],[point[2]]])
        self.theta = theta
        self.empty = [0,0,0]
    
    def rotate_x(self,theta):
        matrix_x = np.array([
            [1, 0, 0],
            [0, math.cos(theta), math.sin(theta)],
            [0, -math.sin(theta), math.cos(theta)]
        ])

        product = np.dot(matrix_x, self.point)
        for i in range(3):
            self.empty[i] = float(product[i])
        
        return product
    
    def rotate_y(self,theta):
        matrix_y = np.array([
            [math.cos(theta), 0, -math.sin(theta)],
            [0, 1, 0],
            [math.sin(theta), 0, math.cos(theta)]
        ])

        product = np.dot(matrix_y, self.point)
        for i in range(3):
            self.empty[i] = float(product[i])
        
        return product

    def rotate_z(self, theta):
        matrix_z = np.array([
            [math.cos(theta), math.sin(theta), 0],
            [-math.sin(theta), math.cos(theta), 0],
            [0, 0, 1]
        ])

        product = np.dot(matrix_z, self.point)
        for i in range(3):
            self.empty[i] = float(product[i])
        
        return product
    
    def translate(self, vector):
        # vector = distance matrix, also in the form of a tuple
        for i in range(3):
            self.empty[i] = float((self.point[i]+vector[i]))
        return tuple(self.empty)
 
class Polygon:
    """
    This class has attributes plot_polygon, transform_polygon  
    """
    def __init__(self, polygon):
        # To avoid following repetitions when rotation or translation involves
        # To use the attributes of the class "Point"
        self.polygon = np.array(polygon).T

    ## Redefine plot function - to plot 3d filled shapes, instead of surfaces

    def rotate(self, convention="zxz", a=0, b=0, c=0):
        # Combine two methods (rotation and translation) - as rotation must be done before translation
        # If not specified, theta = 0, and vector = [0,0,0]
        """
        Transformation contains two parts: first rotation, then translation.
        Rotation uses Euler angles. 6 convensions exist: "zxz", "zyz", "xzx", "xyx", "yxy", "yzy". Default is "zxz" convension.
        Rotation here is anticlockwise, since Dynamo rotates objects in clockwise direction. 
        """
        
        # ROTATION   
        if convention == "zxz":
            matrix = np.array([
                [math.cos(a)*math.cos(c)-math.cos(b)*math.sin(a)*math.sin(c), -math.cos(a)*math.sin(c)-math.cos(b)*math.cos(c)*math.sin(a), math.sin(a)*math.sin(b)],
                [math.cos(c)*math.sin(a)+math.cos(a)*math.cos(b)*math.sin(c), math.cos(a)*math.cos(b)*math.cos(c)-math.sin(a)*math.sin(c), -math.cos(a)*math.sin(b)],
                [math.sin(b)*math.sin(c), math.cos(c)*math.sin(b), math.cos(b)]
            ])

            product = matrix.dot(self.polygon)
        
        elif convention == "zyz":
            matrix = np.array([
                [math.cos(a)*math.cos(b)*math.cos(c)-math.sin(a)*math.sin(c), -math.cos(c)*math.sin(a)-math.cos(a)*math.cos(b)*math.sin(c), math.cos(a)*math.sin(b)],
                [math.cos(a)*math.sin(c)+math.cos(b)*math.cos(c)*math.sin(a), math.cos(a)*math.cos(c)-math.cos(b)*math.sin(a)*math.sin(c), math.sin(a)*math.sin(b)],
                [-math.cos(c)*math.sin(b), math.sin(b)*math.sin(c), math.cos(b)]
            ])

            product = matrix.dot(self.polygon)
        
        elif convention == "yzy":
            matrix = np.array([
                [math.cos(a)*math.cos(b)*math.cos(c)-math.sin(a)*math.sin(c), -math.cos(a)*math.sin(b), math.cos(c)*math.sin(a)+math.cos(a)*math.cos(b)*math.sin(c)],
                [math.cos(c)*math.sin(b), math.cos(b), math.sin(b)*math.sin(c)],
                [-math.cos(a)*math.sin(c)-math.cos(b)*math.cos(c)*math.sin(a), math.sin(a)*math.sin(b), math.cos(a)*math.cos(c)-math.cos(b)*math.sin(a)*math.sin(c)]
            ])

            product = matrix.dot(self.polygon)

        elif convention == "yxy":
            matrix = np.array([
                [math.cos(a)*math.cos(c)-math.cos(b)*math.sin(a)*math.sin(c), math.sin(a)*math.sin(b), math.cos(a)*math.sin(c)+math.cos(b)*math.cos(c)*math.sin(a)],
                [math.sin(b)*math.sin(c), math.cos(b), -math.cos(c)*math.sin(b)],
                [-math.cos(c)*math.sin(a)-math.cos(a)*math.cos(b)*math.sin(c), math.cos(a)*math.sin(b), math.cos(a)*math.cos(b)*math.cos(c)-math.sin(a)*math.sin(c)]
            ])

            product = matrix.dot(self.polygon)

        elif convention == "xyx":
            matrix = np.array([
                [math.cos(b), math.sin(b)*math.sin(c), math.cos(c)*math.sin(b)],
                [math.sin(a)*math.sin(b), math.cos(a)*math.cos(c)-math.cos(b)*math.sin(a)*math.sin(c), -math.cos(a)*math.sin(c)-math.cos(b)*math.cos(c)*math.sin(a)],
                [-math.cos(a)*math.sin(b), math.cos(c)*math.sin(a)+math.cos(a)*math.cos(b)*math.sin(c), math.cos(a)*math.cos(b)*math.cos(c)-math.sin(a)*math.sin(c)]
            ])

            product = matrix.dot(self.polygon)
        
        elif convention == "xzx":
            matrix = np.array([
                [math.cos(b), -math.cos(c)*math.sin(b), math.sin(b)*math.sin(c)],
                [math.cos(a)*math.sin(b), math.cos(a)*math.cos(b)*math.cos(c)-math.sin(a)*math.sin(c), -math.cos(c)*math.sin(a)-math.cos(a)*math.cos(b)*math.sin(c)],
                [math.sin(a)*math.sin(b), math.cos(a)*math.sin(c)+math.cos(b)*math.cos(c)*math.sin(a), math.cos(a)*math.cos(c)-math.cos(b)*math.sin(a)*math.sin(c)]
            ])

            product = matrix.dot(self.polygon)
        return (matrix)
        
        def translate(self, vector = [0,0,0]):
            # TRANSLATION
            product = product.T
            
            # Create a matrix that has same shape as polygon
            n_columns = product.shape[0]
            added = np.zeros((n_columns, 3))

            # change vector into matrix
            for i in range(n_columns):
                added[i] = np.array(vector)
            
            # Do addition
            added = added + product
            
            # Return the the matrix in list form
            transformed = []
            for i in range(added.shape[0]):
                transformed.append([0,0,0])

            flag = 0
            for each in transformed:
                for i in range(3):
                    each[i] = added[flag][i]
                flag += 1
            
            return (transformed)
        

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

"""----------------------------------------------------------------
polygon = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (-1, 0, 0)
)

pol1 = Polygon(polygon).transform_polygon("zxz",a=math.radians(90))
print(pol1) # Good
pol2 = Polygon(polygon).transform_polygon("zxz",a=math.radians(90),b=math.radians(90),c=math.radians(90),vector=[3,3,3])
print(pol2)  
--------------------------------------------------------"""
