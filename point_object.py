import math
import numpy as np


class PointObject:
    def __init__(self, I, J, K):
        self.X = I
        self.Y = J
        self.Z = K

        self.L=[]
        self.R=[]
        self.A=[]

    def translate_to_origin(self, index):
        x0 = self.X[index]
        y0 = self.Y[index]
        z0 = self.Z[index]

        for i in range(len(self.X)):
            self.X[i] -= x0
            self.Y[i] -= y0
            self.Z[i] -= z0

    def reverse_order(self):
        self.X = self.X[::-1]
        self.Y = self.Y[::-1]
        self.Z = self.Z[::-1]

    def find_rz2(self, index):
        return math.atan2(self.X[index], self.Y[index])  # reference angle from Y

    def find_rx2(self, index):
        return -1 * math.atan2(self.Z[index], self.Y[index])  # reference angle from Y

    def find_ry2(self, index):
        return math.atan2(self.Z[index], self.X[index])  # reference angle from X

    def find_rz(self, index):
        return math.atan(self.X[index]/self.Y[index])  # reference angle from Y

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

    def find_bends(self):

        for i in range(0, len(self.X) - 1):
            if i >= len(self.X) - 1:
                self.L.append(0)
                self.R.append(0)
                self.A.append(0)
            elif i <= 0:
                self.L.append(self.calculate_distance(i, i+1))
                self.R.append(0)
                self.A.append(0)
            else:
                self.translate_to_origin(i)
                self.L.append(self.calculate_distance(i, i + 1))

                self.R.append(math.degrees(self.find_ry(i + 1)))

                matrix = self.rotation_matrix(self.find_ry(i + 1), 'y')
                self.rotate(matrix)

                self.A.append(math.degrees(self.find_rz(i + 1)))

                matrix = self.rotation_matrix(self.find_rz(i + 1), 'z')
                self.rotate(matrix)

        for l, r, a in zip(self.L, self.R, self.A):
            print(f"{l:.3f} {r:.3f} {a:.3f}")
        print()
        print()
