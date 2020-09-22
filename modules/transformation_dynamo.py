import numpy as np
import math


class Polygon:
    """
    This class has attributes plot_polygon, transform_polygon  
    """

    def __init__(self):
        polygon = [1,1,1]
        self.polygon = np.array(polygon).T

    def rotate(self, convention="zxz", a=0, b=0, c=0):
        # Combine two methods (rotation and translation) - as rotation must be done before translation
        # If not specified, theta = 0, and vector = [0,0,0]
        """
        Transformation contains two parts: first rotation, then translation.
        Rotation uses Euler angles. 6 conventions exist: "zxz", "zyz", "xzx", "xyx", "yxy", "yzy". Default is "zxz" convention.
        Rotation here is anticlockwise, since Dynamo rotates objects in clockwise direction. 
        """

        # ROTATION   
        matrix = None
        # todo: test
        if convention == "zxz":
            matrix = np.array([
                [math.cos(a) * math.cos(c) - math.cos(b) * math.sin(a) * math.sin(c),
                 -math.cos(a) * math.sin(c) - math.cos(b) * math.cos(c) * math.sin(a), math.sin(a) * math.sin(b)],
                [math.cos(c) * math.sin(a) + math.cos(a) * math.cos(b) * math.sin(c),
                 math.cos(a) * math.cos(b) * math.cos(c) - math.sin(a) * math.sin(c), -math.cos(a) * math.sin(b)],
                [math.sin(b) * math.sin(c), math.cos(c) * math.sin(b), math.cos(b)]
            ])

            # product = matrix.dot(self.polygon)

        elif convention == "zyz":
            matrix = np.array([
                [math.cos(a) * math.cos(b) * math.cos(c) - math.sin(a) * math.sin(c),
                 -math.cos(c) * math.sin(a) - math.cos(a) * math.cos(b) * math.sin(c), math.cos(a) * math.sin(b)],
                [math.cos(a) * math.sin(c) + math.cos(b) * math.cos(c) * math.sin(a),
                 math.cos(a) * math.cos(c) - math.cos(b) * math.sin(a) * math.sin(c), math.sin(a) * math.sin(b)],
                [-math.cos(c) * math.sin(b), math.sin(b) * math.sin(c), math.cos(b)]
            ])

            # product = matrix.dot(self.polygon)

        elif convention == "yzy":
            matrix = np.array([
                [math.cos(a) * math.cos(b) * math.cos(c) - math.sin(a) * math.sin(c), -math.cos(a) * math.sin(b),
                 math.cos(c) * math.sin(a) + math.cos(a) * math.cos(b) * math.sin(c)],
                [math.cos(c) * math.sin(b), math.cos(b), math.sin(b) * math.sin(c)],
                [-math.cos(a) * math.sin(c) - math.cos(b) * math.cos(c) * math.sin(a), math.sin(a) * math.sin(b),
                 math.cos(a) * math.cos(c) - math.cos(b) * math.sin(a) * math.sin(c)]
            ])

            # product = matrix.dot(self.polygon)

        elif convention == "yxy":
            matrix = np.array([
                [math.cos(a) * math.cos(c) - math.cos(b) * math.sin(a) * math.sin(c), math.sin(a) * math.sin(b),
                 math.cos(a) * math.sin(c) + math.cos(b) * math.cos(c) * math.sin(a)],
                [math.sin(b) * math.sin(c), math.cos(b), -math.cos(c) * math.sin(b)],
                [-math.cos(c) * math.sin(a) - math.cos(a) * math.cos(b) * math.sin(c), math.cos(a) * math.sin(b),
                 math.cos(a) * math.cos(b) * math.cos(c) - math.sin(a) * math.sin(c)]
            ])

            # product = matrix.dot(self.polygon)

        elif convention == "xyx":
            matrix = np.array([
                [math.cos(b), math.sin(b) * math.sin(c), math.cos(c) * math.sin(b)],
                [math.sin(a) * math.sin(b), math.cos(a) * math.cos(c) - math.cos(b) * math.sin(a) * math.sin(c),
                 -math.cos(a) * math.sin(c) - math.cos(b) * math.cos(c) * math.sin(a)],
                [-math.cos(a) * math.sin(b), math.cos(c) * math.sin(a) + math.cos(a) * math.cos(b) * math.sin(c),
                 math.cos(a) * math.cos(b) * math.cos(c) - math.sin(a) * math.sin(c)]
            ])

            product = matrix.dot(self.polygon)

        elif convention == "xzx":
            matrix = np.array([
                [math.cos(b), -math.cos(c) * math.sin(b), math.sin(b) * math.sin(c)],
                [math.cos(a) * math.sin(b), math.cos(a) * math.cos(b) * math.cos(c) - math.sin(a) * math.sin(c),
                 -math.cos(c) * math.sin(a) - math.cos(a) * math.cos(b) * math.sin(c)],
                [math.sin(a) * math.sin(b), math.cos(a) * math.sin(c) + math.cos(b) * math.cos(c) * math.sin(a),
                 math.cos(a) * math.cos(c) - math.cos(b) * math.sin(a) * math.sin(c)]
            ])

            product = matrix.dot(self.polygon)
        return matrix
