from tkinter import filedialog
import copy

import numpy as np
from scipy.optimize import fsolve

from point_object import pointObject
import math
import os


class importCoords:
    def __init__(self, figure, canvas):
        # Initialize the Tkinter window
        self.point_objects = []
        self.plotIdx = 0

        # Arrays to store parsed data
        self.i, self.j, self.k = [], [], []

        self.figure, self.canvas = figure, canvas

        self.convertedBool = False

    def calculate_distance(self, idx1, idx2):
        # Calculate Euclidean distance between points at idx1 and idx2
        distance = math.sqrt((self.i[idx2] - self.i[idx1]) ** 2 +
                             (self.j[idx2] - self.j[idx1]) ** 2 +
                             (self.k[idx2] - self.k[idx1]) ** 2)
        return distance

    def segment_points(self):
        segment_ends = []  # Initialize as an empty list, no need for the initial (0, 0) tuple
        threshold_multiplier = 1.05

        for i in range(1, len(self.i)):
            # Calculate the distance between the current point (i) and the point at (i-1)
            distance = self.calculate_distance(i, i - 1)

            if i >= 2:
                # Calculate the threshold based on 1.1 times the distance from point (i-1) and (i-2)
                threshold = threshold_multiplier * self.calculate_distance(i - 1, i - 2)
            else:
                # For the first point, set the threshold to a high value to prevent an out-of-bounds error
                threshold = float('inf')

            # If the distance between the current point and the previous point is greater than the threshold, consider it a segment end
            if distance > threshold:
                # Get the end index of the last segment in segment_ends list
                last_end_idx = segment_ends[-1][1] if segment_ends else -1
                # Append the segment indices as a tuple to segment_ends list, starting from the next index after the last segment
                segment_ends.append((last_end_idx + 1, i - 1))

        # If there are segments, add the last point as a segment end
        if segment_ends:
            segment_ends.append((segment_ends[-1][1] + 1, len(self.i) - 1))

        return segment_ends

    def reorder_segments(self, segment_ends):
        while True:
            # Make a deep copy of the current state
            i_copy, j_copy, k_copy = self.i.copy(), self.j.copy(), self.k.copy()
            reversed_segments = 0  # Variable to track the number of segments reversed in this iteration

            for segment in segment_ends:
                start_idx, end_idx = segment
                if self.should_reverse_segment(start_idx, end_idx):
                    reversed_segment = self.reverse_segment(start_idx, end_idx)
                    i_copy[start_idx:end_idx + 1] = reversed_segment[0]
                    j_copy[start_idx:end_idx + 1] = reversed_segment[1]
                    k_copy[start_idx:end_idx + 1] = reversed_segment[2]
                    reversed_segments += 1  # Increment the count of reversed segments

            # If no segments were reversed, the arrangement is optimized, break the loop
            if reversed_segments == 0:
                break

            # Update the points with the reordered segments
            self.i, self.j, self.k = i_copy, j_copy, k_copy

    def should_reverse_segment(self, start_idx, end_idx):
        # Check if reversing the segment would result in shorter distances between points
        if start_idx <= 1:
            original_distance = self.calculate_distance(end_idx, end_idx + 1)
            reversed_distance = self.calculate_distance(start_idx, end_idx + 1)
        elif end_idx >= len(self.i) - 1:
            original_distance = self.calculate_distance(start_idx - 1, start_idx)
            reversed_distance = self.calculate_distance(start_idx - 1, end_idx)
        else:
            original_distance = (self.calculate_distance(start_idx, start_idx - 1) + self.calculate_distance(end_idx,
                                                                                                             end_idx + 1))
            reversed_distance = self.calculate_distance(start_idx, end_idx) + self.calculate_distance(start_idx,
                                                                                                      end_idx + 1)
        return reversed_distance < original_distance

    def reverse_segment(self, start_idx, end_idx):
        # Reverse the order of points in the segment defined by start_idx and end_idx
        return self.i[start_idx:end_idx + 1][::-1], self.j[start_idx:end_idx + 1][::-1], self.k[start_idx:end_idx + 1][
                                                                                         ::-1]

    def clear_file(self):
        self.point_objects = []
        self.i, self.j, self.k = [], [], []
        self.plotIdx = 0
        self.figure.clear()
        self.convertedBool = False

    def browse_files(self, reorder, filter_straight):
        # Open a file explorer dialog to select a file
        filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                              filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        try:
            # Read the selected file and parse comma-separated values into i, j, and k arrays
            with open(filename, 'r') as file:
                self.clear_file()
                lines = file.readlines()
                for line in lines:
                    values = line.strip().split(',')
                    if len(values) == 3:
                        self.i.append(float(values[0]))
                        self.j.append(float(values[1]))
                        self.k.append(float(values[2]))
        except Exception as e:
            # Handle file reading errors
            print("Error:", e)

        if len(self.i) > 0:

            if reorder == 1:
                # Call segment_points to identify segments
                segment_ends = self.segment_points()
                # Call reorder_segments with segment_ends to reorder the points within each segment
                self.reorder_segments(segment_ends)
            if filter_straight == 1:
                self.filter_straight_sections()

            point_object = pointObject(self.i, self.j, self.k)
            self.point_objects.append(point_object)
            # Create deep copies of the first PointObject instance
            new_point_objects = [copy.deepcopy(self.point_objects[0]) for _ in range(3)]
            # Update point_objects list with the new PointObject instances
            self.point_objects.extend(new_point_objects)
        else:
            print("No data")
        return os.path.basename(filename)

    def filter_straight_sections(self):
        i_filtered, j_filtered, k_filtered = [], [], []

        # Initialize start and end indices of straight segments
        start_idx = 0
        end_idx = 1

        i_filtered.append(self.i[start_idx])
        j_filtered.append(self.j[start_idx])
        k_filtered.append(self.k[start_idx])

        while start_idx < len(self.i) - 2:

            # Find the end index of the current straight segment
            while end_idx < len(self.i) - 1 and self.is_straight_segment(start_idx, end_idx):
                end_idx += 1
            # Add start and end points of the straight segment to filtered lists

            i_filtered.append(self.i[end_idx])
            j_filtered.append(self.j[end_idx])
            k_filtered.append(self.k[end_idx])

            # Move start index to the next potential straight segment
            start_idx = end_idx
            end_idx = end_idx + 1

        if end_idx < len(self.i):
            i_filtered.append(self.i[end_idx])
            j_filtered.append(self.j[end_idx])
            k_filtered.append(self.k[end_idx])

        # Update self.i, self.j, and self.k with filtered values
        self.clear_file()
        self.i, self.j, self.k = i_filtered, j_filtered, k_filtered

    def is_straight_segment(self, start_idx, end_idx):
        angle_threshold_degrees = 1

        # Check if the segment defined by idx and end idx is straight
        # Calculate the angle between the vectors using atan2
        start_vector = (self.i[start_idx + 1] - self.i[start_idx], self.j[start_idx + 1] - self.j[start_idx],
                        self.k[start_idx + 1] - self.k[start_idx])
        next_vector = (self.i[end_idx + 1] - self.i[end_idx], self.j[end_idx + 1] - self.j[end_idx],
                       self.k[end_idx + 1] - self.k[end_idx])

        cross_product = (
            start_vector[1] * next_vector[2] - start_vector[2] * next_vector[1],
            start_vector[2] * next_vector[0] - start_vector[0] * next_vector[2],
            start_vector[0] * next_vector[1] - start_vector[1] * next_vector[0]
        )

        dot_product = sum(a * b for a, b in zip(start_vector, next_vector))
        angle_rad = math.atan2(math.sqrt(sum(c ** 2 for c in cross_product)), dot_product)

        # Convert the threshold from degrees to radians for comparison
        angle_threshold_rad = math.radians(angle_threshold_degrees)

        # Return True if the angle is below the threshold (segment is straight), False otherwise
        return angle_rad < angle_threshold_rad

    # not used
    def get_coord(self, column_index, element_index):
        try:
            # Retrieve the specified element from i, j, or k arrays based on column_index
            if column_index == 'i':
                return self.i[element_index - 1]
            elif column_index == 'j':
                return self.j[element_index - 1]
            elif column_index == 'k':
                return self.k[element_index - 1]
            else:
                return None
        except IndexError:
            # Handle index out of range errors
            return None

    def print_csv(self):
        # Check if there are elements in i, j, and k arrays
        text_array = []
        if len(self.i) > 0 and len(self.j) > 0 and len(self.k) > 0:
            # Iterate through the arrays and print in the specified format
            for i_val, j_val, k_val in zip(self.i, self.j, self.k):
                # print(f"{i_val}, {j_val}, {k_val}")
                text_array.append(f"{i_val}, {j_val}, {k_val}")
        else:
            pass
            # print("No data to print.")
        return text_array

    def convert_coords(self, diameter, pinPos):

        bendDieRadius = 2.5

        if len(self.point_objects) > 0:
            self.point_objects[2].reverse_order_coord()
            self.point_objects[3].reverse_order_coord()
        else:
            # print("No PointObject instances to convert.")
            return

        # minimum extrude distance handling

        for points in self.point_objects:
            i = 1
            while i < len(points.X) - 1:

                if i < len(points.X) - 2:
                    angle1 = self.calculateAngle(points, i)
                    angle2 = self.calculateAngle(points, i + 1)
                else:
                    angle1 = 0
                    angle2 = self.calculateAngle(points, i)

                distanceEuclidian = math.sqrt((points.X[i + 1] - points.X[i]) ** 2 +
                                              (points.Y[i + 1] - points.Y[i]) ** 2 +
                                              (points.Z[i + 1] - points.Z[i]) ** 2)

                arcLengthPrev = .5 * abs(angle2) * (
                        bendDieRadius + diameter / 2)  # 1/2 arc length of next bend in mm
                arcLengthNext = .5 * abs(angle1) * (
                        bendDieRadius + diameter / 2)  # 1/2 arc length of next bend in mm

                if i >= len(points.X) - 2:
                    distance = distanceEuclidian + arcLengthPrev - bendDieRadius
                else:
                    distance = distanceEuclidian - arcLengthPrev + arcLengthNext

                if distance < self.minBendDist(diameter, pinPos, angle2):
                    if i < len(points.X) - 2:
                        del points.X[i+1]
                        del points.Y[i+1]
                        del points.Z[i+1]
                        points.deleted_vertices += 1
                    else:
                        print(f'The end segment of this part needs to be increased in length by {self.minBendDist(diameter, pinPos, angle2) - distance} mm')
                        i += 1
                else:
                    i += 1

        # rotation of other pointObject instances into coordinate systems
        for points in self.point_objects:
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

    def plot3d(self, point_object, title, empty_bool):
        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')

        # Remove default axes
        # ax.set_axis_off()

        if empty_bool:
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_zlim(-1, 1)
            ax.set_box_aspect([2, 2, 2])
            axis_length = 0.5
        else:
            # Set specific axis limits (calculate min and max values)
            x_min = min(point_object.X)
            x_max = max(point_object.X)
            y_min = min(point_object.Y)
            y_max = max(point_object.Y)
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
        ax.set_title(title)

        ax.view_init(elev=30, azim=45)  # isometric view

        if empty_bool:
            self.canvas.draw()
            return

        # Plot points
        ax.scatter(point_object.X, point_object.Y, point_object.Z, c='b', marker='o', label='Points')

        # Draw lines between points
        for i in range(0, len(point_object.X) - 1):
            ax.plot([point_object.X[i], point_object.X[i + 1]],
                    [point_object.Y[i], point_object.Y[i + 1]],
                    [point_object.Z[i], point_object.Z[i + 1]], c='black')

        # Redraw the canvas
        self.canvas.draw()

    def calculate_bends(self, material, diameter, pinPos):
        for points in self.point_objects:
            points.find_bends(diameter)
            points.springBack(material)
#            points.filterCloseVertices(diameter, pinPos)
            points.angleSolver(diameter, pinPos)

    def incrementIdx(self):
        if self.plotIdx >= 3:
            self.plotIdx = 0
        else:
            self.plotIdx += 1

    def next(self):
        self.update_gui()

    def update_gui(self):
        # Update GUI elements here
        # print("Coordinates Converted")

        self.plot3d(self.point_objects[self.plotIdx], f'Bend Orientation {self.plotIdx + 1}', False)
        # print(f"PointObject {self.plotIdx + 1} coordinates:")
        # self.point_objects[self.plotIdx].print_contents()
        # print()  # Add an empty line for better readability between PointObjects

    # calculates the minimum extrusion lenth required to make a bend based off the bender settings and angle
    @staticmethod
    def minBendDist(diameter, pinPos, angle):

        bendPin = 6
        offset = .8

        bendDieRadius = 2.5

        arcLength = abs(angle) * (bendDieRadius + diameter / 2)

        angle = abs(angle)
        # print("Springback , desired angle")
        # print(self.SA[i], angle)

        x0 = (2.5 + diameter) * np.sin(angle) + offset
        y0 = (2.5 + diameter) * np.cos(angle) - (2.5 + diameter / 2)

        a = np.tan(angle) * -1
        b = -1
        c = y0 - a * x0

        def func(x):
            return [np.absolute(a * x[0] + b * x[1] + c) / np.sqrt(a ** 2 + b ** 2) - bendPin / 2,
                    np.sqrt(x[0] ** 2 + x[1] ** 2) - pinPos]

        # better initial guesses using the circle of the pin path
        xGuess = pinPos * np.cos(angle - (0.2762 + .81 * angle / np.pi))
        yGuess = pinPos * -1 * np.sin(angle - (0.2762 + .81 * angle / np.pi))

        root = fsolve(func, [xGuess, yGuess])

        distance = math.dist(root, [x0, y0]) + arcLength

        return distance

    # returns angle between two segments in radians given an intersection index and a pointObject instance
    @staticmethod
    def calculateAngle(pointObject, idx):

        # Calculate the angle between the vectors using atan2
        start_vector = (pointObject.X[idx] - pointObject.X[idx - 1], pointObject.Y[idx] - pointObject.Y[idx - 1],
                        pointObject.Z[idx] - pointObject.Z[idx - 1])
        next_vector = (pointObject.X[idx + 1] - pointObject.X[idx], pointObject.Y[idx + 1] - pointObject.Y[idx],
                       pointObject.Z[idx + 1] - pointObject.Z[idx])

        cross_product = (
            start_vector[1] * next_vector[2] - start_vector[2] * next_vector[1],
            start_vector[2] * next_vector[0] - start_vector[0] * next_vector[2],
            start_vector[0] * next_vector[1] - start_vector[1] * next_vector[0]
        )

        dot_product = sum(a * b for a, b in zip(start_vector, next_vector))
        return math.atan2(math.sqrt(sum(c ** 2 for c in cross_product)), dot_product)
