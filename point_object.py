"""
This class contains all the data for the coordinates of a point_object and its bend variables (L, R, A, MA)
This class also contains all the methods for the first step of transforming the coordinates to expected position,
and calculating length, rotation, and bend angle values while checking for collisions.


Build:
    pyinstaller --onefile --noconsole --collect-data sv_ttk WireBenderCAM.py

Recommended:
    Python 3.10
    pip: -r requirements.txt

Anderson Boyer
"""

import math
import numpy as np

class PointObject:
    """
    L = Length of segment
    R = Rotation of segment to make next bend
    A = Angle of Bend
    MA = Motor Angle for a particular bend, populated in apply_compensation()
    """
    def __init__(self, x, y, z):
        self.X, self.Y, self.Z = x, y, z
        self.L, self.R, self.A, self.MA = [], [], [], []
        self.collision_count = 0
        self.deleted_vertices = 0
        self.pin_pos = 0.0

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
        if self.X[index] == 0.0:
            return math.pi/2
        return math.atan(self.Z[index] / self.X[index])  # reference angle from X

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

    def calculate_distance(self, index1, index2):
        if index1 < 0 or index1 >= len(self.X) or index2 < 0 or index2 >= len(self.X):
            return None

        # Calculate Euclidean distance between points at index1 and index2
        distance = math.sqrt((self.X[index2] - self.X[index1]) ** 2 +
                             (self.Y[index2] - self.Y[index1]) ** 2 +
                             (self.Z[index2] - self.Z[index1]) ** 2)
        return distance

    def find_bends(self, diameter):

        x_copy, y_copy, z_copy = self.X.copy(), self.Y.copy(), self.Z.copy()
        bend_die_radius = 2.5

        for i in range(len(self.X)):
            if i >= len(self.X) - 1:  # last point
                # for the first point, extrusion length will be equal to L + 1/2 the arc length of next bend -
                # 2.5mm (bend die radius)
                arc_length = .5 * abs(math.radians(self.A[-1])) * (bend_die_radius + diameter / 2)  # 1/2 arc length
                # of next bend in mm
                self.L.append(self.calculate_distance(i - 1, i) + arc_length - bend_die_radius)
                # for the first point, extrusion length will be equal to L + 1/2 the arc length of next bend + 2.5mm
                # (bend die radius)
                self.R.append(0)
                self.X, self.Y, self.Z = x_copy, y_copy, z_copy
            elif i <= 0:  # first point
                self.L.append(0)
                self.A.append(0)
            else:

                self.collision_detection(i)

                self.translate_to_origin(i)

                self.collision_detection(i + 1)

                self.R.append(math.degrees(self.find_ry(i + 1)))
                matrix = self.rotation_matrix(self.find_ry(i + 1), 'y')
                self.rotate(matrix)

                self.collision_detection(i + 1)

                arc_length_prev = .5 * abs(self.find_rz2(i + 1)) * (bend_die_radius + diameter / 2)  # 1/2 arc length
                # of prev bend in mm
                arc_length_next = .5 * abs(math.radians(self.A[-1])) * (bend_die_radius + diameter / 2)  # 1/2 arc
                # length of next bend in mm
                if i < len(self.X) - 2:  # only add L if this is not the last bend
                    self.L.append(self.calculate_distance(i, i + 1) - arc_length_prev + arc_length_next)

                self.A.append(math.degrees(self.find_rz2(i + 1)))
                matrix = self.rotation_matrix(self.find_rz2(i + 1), 'z')
                self.rotate(matrix)

                self.collision_detection(i + 1)

        if len(self.A) > 1:
            # for the last point, extrusion length will be equal to L - 1/2 the arc length of next
            # bend + 2.5mm (bend die radius)
            arc_length = .5 * abs(math.radians(self.A[1])) * (bend_die_radius + diameter / 2)  # 1/2 arc length of
            # next bend in mm
            # bend die radius subtracted here because we assume the user cuts the part off flush with the bend die
            self.L[0] = self.calculate_distance(0, 1) - arc_length + bend_die_radius

        self.reverse_order_bends()

    def collision_detection(self, start_index):
        # collision area in mm
        # coordinate system same as machine
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
        return [(round(length, 3), round(rotation, 3), round(angle, 3), round(motor_angle, 3)) for length,
                rotation, angle, motor_angle in zip(self.L, self.R, self.A, self.MA)]

    def apply_compensation(self, compensation_coeff):
        for i in range(len(self.A)):
            if self.A[i] < -.05:
                self.MA.append(-1 * np.polyval(compensation_coeff, abs(self.A[i])))
            elif self.A[i] > .05:
                self.MA.append(np.polyval(compensation_coeff, abs(self.A[i])))
            else:
                self.MA.append(0.0)
