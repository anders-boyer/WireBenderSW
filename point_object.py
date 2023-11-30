import math
import numpy as np
from scipy.optimize import fsolve

class pointObject:

    def __init__(self, I, J, K):
        self.X, self.Y, self.Z = I, J, K
        self.L, self.R, self.A, self.SA, self.MA = [], [], [], [], []
        self.collision_count = 0
        self.deleted_vertices = 0

    def translate_to_origin(self, index):
        x0, y0, z0 = self.X[index], self.Y[index], self.Z[index]

        for i in range(len(self.X)):
            self.X[i] -= x0
            self.Y[i] -= y0
            self.Z[i] -= z0

    def reverse_order_coord(self):
        self.X = self.X[::-1]
        self.Y = self.Y[::-1]
        self.Z = self.Z[::-1]

    def reverse_order_bends(self):
        self.L = self.L[::-1]
        self.R = self.R[::-1]
        self.A = self.A[::-1]

    def find_rz2(self, index):
        return math.atan2(self.X[index], self.Y[index])  # reference angle from Y

    def find_rx2(self, index):
        return -1 * math.atan2(self.Z[index], self.Y[index])  # reference angle from Y

    def find_ry2(self, index):
        if index < len(self.Z):
            return math.atan2(self.Z[index], self.X[index])  # reference angle from X
        else:
            print("Array size too small for conversion after minimum bend checking")
            return 0

    def find_ry(self, index):
        return math.atan(self.Z[index]/self.X[index])  # reference angle from X

    @staticmethod
    def rotation_matrix(radians, axis):
        matrix = np.zeros((3, 3))
        if axis == 'x':
            matrix = np.array([[1, 0, 0],
                               [0, math.cos(radians), -1 * math.sin(radians)],
                               [0, math.sin(radians), math.cos(radians)]])
        elif axis == 'y':
            matrix = np.array([[math.cos(radians), 0, math.sin(radians)],
                               [0, 1, 0],
                               [-1 * math.sin(radians), 0, math.cos(radians)]])
        elif axis == 'z':
            matrix = np.array([[math.cos(radians), -math.sin(radians), 0],
                               [math.sin(radians), math.cos(radians), 0],
                               [0, 0, 1]])
        return matrix

    def rotate(self, matrix):

        # Create 3x1 column vectors for x, y, z arrays
        vectors = np.vstack((self.X, self.Y, self.Z))
        # Perform matrix multiplication
        rotated_vectors = np.dot(matrix, vectors)
        # Update x, y, z arrays with the rotated vectors
        self.X, self.Y, self.Z = rotated_vectors

    def print_contents(self):
        for x, y, z in zip(self.X, self.Y, self.Z):
            print(f"{x:.3f} {y:.3f} {z:.3f}")

    # not used
    # def find_next_bend(self, indexStart):
    #     for i in range(indexStart, len(self.X) - 2):
    #         # Calculate cross product for segments (i, i+1) and (i+1, i+2)
    #         cross_product = np.cross([self.X[i + 1] - self.X[i], self.Y[i + 1] - self.Y[i], self.Z[i + 1] - self.Z[i]]
    #         , [self.X[i + 2] - self.X[i + 1], self.Y[i + 2] - self.Y[i + 1], self.Z[i + 2] - self.Z[i + 1]])
    #         # Check if the cross product indicates a bend
    #         if np.linalg.norm(cross_product) > 0.05:
    #             return i + 1  # Return the index of the first point in the bend
    #     # If no bend is found, return the last index
    #     return len(self.X) - 1

    def calculate_distance(self, index1, index2):
        if index1 < 0 or index1 >= len(self.X) or index2 < 0 or index2 >= len(self.X):
            return None

        # Calculate Euclidean distance between points at index1 and index2
        distance = math.sqrt((self.X[index2] - self.X[index1])**2 +
                             (self.Y[index2] - self.Y[index1])**2 +
                             (self.Z[index2] - self.Z[index1])**2)
        return distance

    def find_bends(self, diameter):

        Xcopy, Ycopy, Zcopy = self.X.copy(), self.Y.copy(), self.Z.copy()
        bendDieRadius = 2.5

        for i in range(len(self.X)):
            if i >= len(self.X) - 1:  # last point

                # for l, r, a in zip(self.L, self.R, self.A):
                #     print(f"{l:.3f} {r:.3f} {a:.3f}")
                # print()
                # print()

                # for the first point, extrusion length will be equal to L + 1/2 the arc length of next bend - 2.5mm (bend die radius)\
                arcLength = .5 * abs(math.radians(self.A[-1])) * (bendDieRadius + diameter / 2)  # 1/2 arc length of next bend in mm

                self.L.append(self.calculate_distance(i-1, i) + arcLength - bendDieRadius)

                # for the first point, extrusion length will be equal to L + 1/2 the arc length of next bend + 2.5mm (bend die radius)

                self.R.append(0)
                self.X, self.Y, self.Z = Xcopy, Ycopy, Zcopy
            elif i <= 0:  # first point
                self.L.append(0)
                self.A.append(0)
            else:

                self.collision_detection(i)

                self.translate_to_origin(i)

                self.collision_detection(i+1)

                self.R.append(math.degrees(self.find_ry(i + 1)))

                matrix = self.rotation_matrix(self.find_ry(i + 1), 'y')
                self.rotate(matrix)
                self.collision_detection(i+1)

                arcLengthPrev = .5 * abs(self.find_rz2(i + 1)) * (bendDieRadius + diameter / 2)  # 1/2 arc length of next bend in mm
                arcLengthNext = .5 * abs(math.radians(self.A[-1])) * (bendDieRadius + diameter / 2)  # 1/2 arc length of next bend in mm

                if i < len(self.X) - 2: #only add L if this is not the last bend
                    self.L.append(self.calculate_distance(i, i + 1)-arcLengthPrev+arcLengthNext)

                self.A.append(math.degrees(self.find_rz2(i + 1)))

                matrix = self.rotation_matrix(self.find_rz2(i + 1), 'z')
                self.rotate(matrix)
                self.collision_detection(i+1)


        if len(self.A) > 1:
            # for the last point, extrusion length will be equal to L - 1/2 the arc length of next bend + 2.5mm (bend die radius)
            arcLength = .5 * abs(math.radians(self.A[1])) * (bendDieRadius + diameter / 2)  # 1/2 arc length of next bend in mm
            # bend die radius subtracted here because we assume the user cuts the part off flush with the bend die
            self.L[0] = self.calculate_distance(0, 1) - arcLength + bendDieRadius

        self.reverse_order_bends()

    def collision_detection(self, start_index):

        # collision zone in mm
        limits = {
            'x': [-150, 150],
            'y': [-1000, -5],
            'z': [-100, -5]
        }

        # Check if any point past the start_index lies inside the cube
        for i in range(start_index, len(self.X)):
            point = [self.X[i], self.Y[i], self.Z[i]]
            if self.point_inside_cube(point, limits):
                self.collision_count += 1
                return True  # Collision detected

        return False  # No collision

    @staticmethod
    def point_inside_cube(point, limits):
        """
        Check if a point lies inside a cube defined by its x y and z limits
        """
        x, y, z = point
        x_min, x_max = limits['x']
        y_min, y_max = limits['y']
        z_min, z_max = limits['z']

        if (x_min < x < x_max) & (y_min < y < y_max) & (z_min < z < z_max):
            return True  # Point lies inside the cube

        return False  # Point does not lie inside the cube

    def get_lra_data(self):
        # Assuming you have arrays named L, R, and A
        return [(round(l, 3), round(r, 3), round(a, 3), round(sa, 3), round(ma, 3)) for l, r, a, sa, ma in zip(self.L, self.R, self.A, self.SA, self.MA)]

    def springBack(self, material):
        for i in range(len(self.A)):
            if self.A[i] < -.05:
                self.SA.append(self.A[i] - 1)
            elif self.A[i] > .05:
                self.SA.append(self.A[i] + 1)
            else:
                self.SA.append(0)

    # def angleSolver(self, diameter, pinPos):
    #
    #     bendPin = 6
    #     offset = .8
    #     minThreshold = 0.05
    #
    #     for i in range(len(self.A)):
    #
    #         # skip if angle is below threshold
    #         if abs(self.A[i]) < minThreshold:
    #             self.MA.append(0)
    #             continue
    #
    #         angle = abs(math.radians(self.SA[i]))
    #         # print("Springback , desired angle")
    #         # print(self.SA[i], angle)
    #
    #         x0 = (2.5 + diameter) * np.sin(angle) + offset
    #         y0 = (2.5 + diameter) * np.cos(angle) - (2.5 + diameter / 2)
    #
    #         a = np.tan(angle) * -1
    #         b = -1
    #         c = y0 - a * x0
    #
    #         def func(x):
    #             return [np.absolute(a * x[0] + b * x[1] + c) / np.sqrt(a ** 2 + b ** 2) - bendPin / 2,
    #                     np.sqrt(x[0] ** 2 + x[1] ** 2) - pinPos]
    #
    #         # better initial guesses using the circle of the pin path
    #         xGuess = pinPos * np.cos(angle - (0.2762 + .81 * angle / np.pi))
    #         yGuess = pinPos * -1 * np.sin(angle - (0.2762 + .81 * angle / np.pi))
    #         # print(" x , y guess")
    #         # print(xGuess, yGuess)
    #
    #         root = fsolve(func, [xGuess, yGuess])
    #         # print("root")
    #         # print(root)
    #         motorangle = math.atan2(root[1], root[0]) * 180 / np.pi
    #         # print("motor angle", motorangle)
    #
    #         # Positive bends
    #         if self.A[i] > 0:
    #             self.MA.append(-1 * motorangle)
    #         # Negative bends
    #         elif self.A[i] < 0:
    #             self.MA.append(motorangle)

    # def filterCloseVertices(self, diameter, pinPos):
    #     # self.Lcopy, self.Rcopy, self.SAcopy = self.L.copy(), self.R.copy(), self.SA.copy()
    #     i = 0
    #
    #     while i < len(self.A)-1:
    #         if self.L[i] < self.minBendDist(diameter, pinPos, self.SA[i]):
    #             self.L[i] += self.L[i + 1]
    #             self.R[i] += self.R[i + 1]
    #             self.A[i] += self.A[i + 1]
    #             self.SA[i] += self.SA[i+1] # should probably add something here that recalculates springback based on new desired angle
    #             del self.L[i + 1]
    #             del self.R[i + 1]
    #             del self.A[i + 1]
    #             del self.SA[i + 1]
    #             self.deleted_vertices += 1
    #         else:
    #             i += 1

        # self.L, self.R, self.A, self.SA, self.MA = [], [], [], [], []

    # @staticmethod
    # def minBendDist(diameter, pinPos, angle):
    #
    #     bendPin = 6
    #     offset = .8
    #
    #     bendDieRadius = 2.5
    #
    #     arcLength = abs(math.radians(angle)) * (bendDieRadius + diameter / 2)
    #
    #     angle = abs(math.radians(angle))
    #     # print("Springback , desired angle")
    #     # print(self.SA[i], angle)
    #
    #     x0 = (2.5 + diameter) * np.sin(angle) + offset
    #     y0 = (2.5 + diameter) * np.cos(angle) - (2.5 + diameter / 2)
    #
    #     a = np.tan(angle) * -1
    #     b = -1
    #     c = y0 - a * x0
    #
    #     def func(x):
    #         return [np.absolute(a * x[0] + b * x[1] + c) / np.sqrt(a ** 2 + b ** 2) - bendPin / 2,
    #                 np.sqrt(x[0] ** 2 + x[1] ** 2) - pinPos]
    #
    #     # better initial guesses using the circle of the pin path
    #     xGuess = pinPos * np.cos(angle - (0.2762 + .81 * angle / np.pi))
    #     yGuess = pinPos * -1 * np.sin(angle - (0.2762 + .81 * angle / np.pi))
    #
    #     root = fsolve(func, [xGuess, yGuess])
    #
    #     return math.dist(root, [x0, y0]) + arcLength






