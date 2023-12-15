"""""
This class represents the first destination of the data from the CSV file.

It contains methods for opening the file browser and reading the file from it,
plotting the coordinates, and transforming the coordinates into our coordinate systems.

It also contains the point_objects instance variable which is an array containing four point_object instances.
The four instances represent the four possible bend orientations for a single part. This class also contains methods
to loop through that array and call the same methods on all bend orientations.

Anderson Boyer
"""


from tkinter import filedialog
import copy
import numpy as np
from scipy.optimize import fsolve
from point_object import PointObject
import math
import os


class ImportCoords:
    def __init__(self, figure, canvas):
        # Initialize the Tkinter window
        self.point_objects = []
        self.plotIdx = 0
        # Arrays to store parsed data
        self.x, self.y, self.z = [], [], []
        self.figure, self.canvas = figure, canvas
        self.convertedBool = False
        self.compensation_coeff = np.zeros(2)

    def clear_file(self):
        self.point_objects = []
        self.x, self.y, self.z = [], [], []
        self.plotIdx = 0
        self.figure.clear()
        self.convertedBool = False
        self.compensation_coeff = np.zeros(2)

    def browse_files(self):
        # Open a file explorer dialog to select a file
        filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                              filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        try:
            # Read the selected file and parse comma-separated values into i, j, and k arrays
            with open(filename, 'r') as file:
                self.clear_file()
                lines = file.readlines()
                for line in lines:
                    values = line.strip().split(',')
                    if len(values) == 3:
                        self.x.append(float(values[0]))
                        self.y.append(float(values[1]))
                        self.z.append(float(values[2]))
                    else:
                        print("CSV must have 3 columns")
                        break
        except Exception as e:
            # Handle file reading errors
            print("Error:", e)

        if len(self.x) > 0:
            point_object = PointObject(self.x, self.y, self.z)
            self.point_objects.append(point_object)
            # Create deep copies of the first PointObject instance
            new_point_objects = [copy.deepcopy(self.point_objects[0]) for _ in range(3)]
            # Update point_objects list with the new PointObject instances
            self.point_objects.extend(new_point_objects)
        else:
            print("No data")
        return os.path.basename(filename)

    def print_csv(self):
        # Check if there are elements in i, j, and k arrays
        text_array = []
        if len(self.x) > 0 and len(self.y) > 0 and len(self.z) > 0:
            # Iterate through the arrays and print in the specified format
            for i_val, j_val, k_val in zip(self.x, self.y, self.z):
                text_array.append(f"{i_val}, {j_val}, {k_val}")
        else:
            pass
            print("No data to print.")
        return text_array

    def convert_coords(self, diameter, pin_pos):

        bend_die_radius = 2.5

        if len(self.point_objects) > 0:
            self.point_objects[2].reverse_order_coord()
            self.point_objects[3].reverse_order_coord()
        else:
            print("No PointObject instances to convert.")
            return

        # minimum extrude distance handling
        for points in self.point_objects:
            i = 1
            while i < len(points.X) - 1:

                if i < len(points.X) - 2:
                    angle1 = self.calculate_angle(points, i)
                    angle2 = self.calculate_angle(points, i + 1)
                else:
                    angle1 = 0
                    angle2 = self.calculate_angle(points, i)

                distance_euclidian = math.sqrt((points.X[i + 1] - points.X[i]) ** 2 +
                                               (points.Y[i + 1] - points.Y[i]) ** 2 +
                                               (points.Z[i + 1] - points.Z[i]) ** 2)

                arc_length_prev = .5 * abs(angle2) * (
                        bend_die_radius + diameter / 2)  # 1/2 arc length of next bend in mm
                arc_length_next = .5 * abs(angle1) * (
                        bend_die_radius + diameter / 2)  # 1/2 arc length of next bend in mm

                if i >= len(points.X) - 2:
                    distance = distance_euclidian + arc_length_prev - bend_die_radius
                else:
                    distance = distance_euclidian - arc_length_prev + arc_length_next

                if distance < (self.min_bend_dist(diameter, pin_pos, angle2)):
                    if i < len(points.X) - 2:
                        del points.X[i + 1]
                        del points.Y[i + 1]
                        del points.Z[i + 1]
                        points.deleted_vertices += 1
                    else:
                        i += 1
                        self.extend_last_point(points, distance)

                else:
                    i += 1

        # rotation of other pointObject instances into coordinate systems
        for points in self.point_objects:
            points.pin_pos = pin_pos
            points.translate_to_origin(0)

            rotation_matrix = points.rotation_matrix(points.find_rz2(1), 'z')
            points.rotate(rotation_matrix)

            rotation_matrix = points.rotation_matrix(points.find_rx2(1), 'x')
            points.rotate(rotation_matrix)

            rotation_matrix = points.rotation_matrix(points.find_ry2(2), 'y')
            points.rotate(rotation_matrix)

        rotation_matrix = self.point_objects[0].rotation_matrix(math.pi, 'y')

        self.point_objects[1].rotate(rotation_matrix)
        self.point_objects[3].rotate(rotation_matrix)

        self.convertedBool = True
        self.update_gui()

    @staticmethod
    def extend_last_point(point_object, distance):
        # Ensure the arrays have the same length
        if len(point_object.X) == len(point_object.Y) == len(point_object.Z) and len(point_object.X) >= 2:
            # Calculate the direction vector between the last and second-to-last points
            direction_vector = np.array(
                [point_object.X[-1] - point_object.X[-2], point_object.Y[-1] - point_object.Y[-2],
                 point_object.Z[-1] - point_object.Z[-2]])

            # Normalize the direction vector
            direction_vector /= np.linalg.norm(direction_vector)

            # Extend the last point along the direction vector by the specified distance
            extended_point = np.array(
                [point_object.X[-1], point_object.Y[-1], point_object.Z[-1]]) + distance * direction_vector

            # Update the last point in the arrays
            point_object.X[-1], point_object.Y[-1], point_object.Z[-1] = extended_point
        else:
            print("Error: Arrays must have the same length and contain at least two points.")

    def plot3d(self, point_object, title, empty_bool, dark_theme=True):
        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')

        if dark_theme:
            ax.set_facecolor('#1e1e1e')  # Background color
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False

            ax.grid(False)
            ax.set_title(title, color='white', fontsize=20)  # Set title color to white

            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.zaxis.label.set_color('white')

            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.tick_params(axis='z', colors='white')

        if empty_bool:
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_zlim(-1, 1)
            ax.set_box_aspect([2, 2, 2])
            axis_length = 0.5
        else:
            # Set specific axis limits (calculate min and max values)
            x_min = min(point_object.X)
            x_max = max(point_object.X) + .01
            y_min = min(point_object.Y)
            y_max = max(point_object.Y) + .01
            z_min = min(point_object.Z)
            z_max = max(point_object.Z) + .01

            # Set axis limits
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_zlim(z_min, z_max)
            # Disable automatic scaling and set equal aspect ratio for all dimensions
            ax.set_box_aspect([abs(x_max - x_min), abs(y_max - y_min), abs(z_max - z_min)])

            axis_length = max(point_object.Y) * 0.4

        ax.plot([0, axis_length], [0, 0], [0, 0], color='red', linewidth=2, label='X-Axis')
        ax.plot([0, 0], [0, axis_length], [0, 0], color='green', linewidth=2, label='Y-Axis')
        ax.plot([0, 0], [0, 0], [0, axis_length], color='blue', linewidth=2, label='Z-Axis')

        # Set labels and title
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')

        ax.view_init(elev=30, azim=45)  # isometric view

        if empty_bool:
            self.canvas.draw()
            return

        # Plot points
        ax.scatter(point_object.X, point_object.Y, point_object.Z, c='black', marker='o', label='Points')

        # Draw lines between points
        for i in range(0, len(point_object.X) - 1):
            ax.plot([point_object.X[i], point_object.X[i + 1]],
                    [point_object.Y[i], point_object.Y[i + 1]],
                    [point_object.Z[i], point_object.Z[i + 1]], c='white', linewidth=4)

        # Redraw the canvas
        self.canvas.draw()

    def calculate_bends(self, material_file, diameter):
        self.compute_compensation_coefficients(material_file)

        for points in self.point_objects:
            points.find_bends(diameter)
            points.apply_compensation(self.compensation_coeff)

    def update_gui(self):
        self.plot3d(self.point_objects[self.plotIdx], f'Bend Orientation {self.plotIdx + 1}', False)

    # calculates the minimum extrusion length required to make a bend based off the bender settings and angle
    @staticmethod
    def min_bend_dist(diameter, pin_pos, angle):

        bend_pin = 6
        offset = .8
        bend_die_radius = 2.5
        arc_length = abs(angle) * (bend_die_radius + diameter / 2)

        angle = abs(angle)

        x0 = (2.5 + diameter) * np.sin(angle) + offset
        y0 = (2.5 + diameter) * np.cos(angle) - (2.5 + diameter / 2)

        a = np.tan(angle) * -1
        b = -1
        c = y0 - a * x0

        def func(x):
            return [np.absolute(a * x[0] + b * x[1] + c) / np.sqrt(a ** 2 + b ** 2) - bend_pin / 2,
                    np.sqrt(x[0] ** 2 + x[1] ** 2) - pin_pos]

        # better initial guesses using the circle of the pin path
        x_guess = pin_pos * np.cos(angle - (0.2762 + .81 * angle / np.pi))
        y_guess = pin_pos * -1 * np.sin(angle - (0.2762 + .81 * angle / np.pi))

        root = fsolve(func, [x_guess, y_guess])

        distance = math.dist(root, [x0, y0]) + arc_length

        return distance

    # returns angle between two segments in radians given an intersection index and a pointObject instance
    @staticmethod
    def calculate_angle(point_object, idx):

        # Calculate the angle between the vectors using atan2
        start_vector = (point_object.X[idx] - point_object.X[idx - 1], point_object.Y[idx] - point_object.Y[idx - 1],
                        point_object.Z[idx] - point_object.Z[idx - 1])
        next_vector = (point_object.X[idx + 1] - point_object.X[idx], point_object.Y[idx + 1] - point_object.Y[idx],
                       point_object.Z[idx + 1] - point_object.Z[idx])

        cross_product = (
            start_vector[1] * next_vector[2] - start_vector[2] * next_vector[1],
            start_vector[2] * next_vector[0] - start_vector[0] * next_vector[2],
            start_vector[0] * next_vector[1] - start_vector[1] * next_vector[0]
        )

        dot_product = sum(a * b for a, b in zip(start_vector, next_vector))
        return math.atan2(math.sqrt(sum(c ** 2 for c in cross_product)), dot_product)

    # returns array of compensation coefficients given a filename
    # x is the desired angle, y is the motor angle (MA)
    def compute_compensation_coefficients(self, filename):
        filepath = os.path.join("Materials", filename)
        # Load csv
        compensation_data = np.loadtxt(filepath, delimiter=",", dtype=str)
        compensation_data = compensation_data.astype(float)

        best_fit = np.polyfit(compensation_data[:, 1], compensation_data[:, 0], 3)

        self.compensation_coeff = best_fit
