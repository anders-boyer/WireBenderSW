# create a virtual environment for your interpreter and install these packages:
# use python 3.9
# pip install -r requirements.txt
# or
# pip install mayavi
# pip install PyQt6
# pip install PySide2

from tkinter import *
from tkinter import filedialog
import copy
from mayavi import mlab
from point_object import PointObject
import math
import os
import numpy as np


class GUI:
    def __init__(self, root):
        # Initialize the Tkinter window
        self.root = root
        self.point_objects = []

        # Arrays to store parsed data
        self.i = []
        self.j = []
        self.k = []

        # Create a label for the file explorer
        self.label_file_explorer = Label(root, text="Import File", width=100, height=4, fg="blue")
        self.label_file_explorer.grid(column=1, row=1)
        # Create a 'Browse Files' button and associate it with the browse_files method
        self.button_explore = Button(root, text="Browse Files", command=self.browse_files)
        self.button_explore.grid(column=1, row=2)
        # Create an 'Exit' button and associate it with the exit method
        self.button_exit = Button(root, text="Exit", command=exit)
        self.button_exit.grid(column=1, row=5)
        self.button_calculate_bends = Button(root, text="Calculate Bends", command=self.calculate_bends)
        self.button_calculate_bends.grid(column=1, row=6)


    def calculate_distance(self, idx1, idx2):
        # Calculate Euclidean distance between points at idx1 and idx2
        distance = math.sqrt((self.i[idx2] - self.i[idx1])**2 +
                             (self.j[idx2] - self.j[idx1])**2 +
                             (self.k[idx2] - self.k[idx1])**2)
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
            i_copy, j_copy, k_copy = self.i[:], self.j[:], self.k[:]
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
            original_distance = (self.calculate_distance(start_idx, start_idx - 1) + self.calculate_distance(end_idx, end_idx + 1))
            reversed_distance = self.calculate_distance(start_idx, end_idx) + self.calculate_distance(start_idx, end_idx + 1)
        return reversed_distance < original_distance

    def reverse_segment(self, start_idx, end_idx):
        # Reverse the order of points in the segment defined by start_idx and end_idx
        return self.i[start_idx:end_idx + 1][::-1], self.j[start_idx:end_idx + 1][::-1], self.k[start_idx:end_idx + 1][::-1]

    def clear_file(self):
        self.point_objects = []
        self.i = []
        self.j = []
        self.k = []

    def browse_files(self):
        self.clear_file()
        # Open a file explorer dialog to select a file
        filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                              filetypes=( ("Text files", "*.txt"), ("All files", "*.*")))
        try:
            # Read the selected file and parse comma-separated values into i, j, and k arrays
            with open(filename, 'r') as file:
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
            # Call segment_points to identify segments
            segment_ends = self.segment_points()
            # Call reorder_segments with segment_ends to reorder the points within each segment
            self.reorder_segments(segment_ends)

            self.filter_straight_sections()

            point_object = PointObject(self.i, self.j, self.k)
            self.point_objects.append(point_object)
            # Create deep copies of the first PointObject instance
            new_point_objects = [copy.deepcopy(self.point_objects[0]) for _ in range(3)]
            # Update point_objects list with the new PointObject instances
            self.point_objects.extend(new_point_objects)
        else:
            print("No data")

        # Update the label to show the opened file
        self.label_file_explorer.configure(text="Ready to Convert Coordinates: " + os.path.basename(filename))

    def filter_straight_sections(self):
        i_filtered, j_filtered, k_filtered = [], [], []

        # Initialize start and end indices of straight segments
        start_idx = 0
        end_idx = 1

        i_filtered.append(self.i[start_idx])
        j_filtered.append(self.j[start_idx])
        k_filtered.append(self.k[start_idx])
        while start_idx < len(self.i) - 3:

            # Find the end index of the current straight segment
            while end_idx <= len(self.i) - 2 and self.is_straight_segment(start_idx, end_idx):
                end_idx += 1
            # Add start and end points of the straight segment to filtered lists

            i_filtered.append(self.i[end_idx])
            j_filtered.append(self.j[end_idx])
            k_filtered.append(self.k[end_idx])

            # Move start index to the next potential straight segment
            start_idx = end_idx
            end_idx = end_idx + 1

        # Update self.i, self.j, and self.k with filtered values
        self.clear_file()
        self.i, self.j, self.k = i_filtered, j_filtered, k_filtered

    def is_straight_segment(self, start_idx, end_idx):
        angle_threshold_degrees = 0.2

        # Check if the segment defined by idx and end idx is straight
        # Calculate the angle between the vectors using atan2
        start_vector = (self.i[start_idx + 1] - self.i[start_idx], self.j[start_idx + 1] - self.j[start_idx], self.k[start_idx + 1] - self.k[start_idx])
        next_vector = (self.i[end_idx + 1] - self.i[end_idx], self.j[end_idx + 1] - self.j[end_idx], self.k[end_idx + 1] - self.k[end_idx])

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
        if len(self.i) > 0 and len(self.j) > 0 and len(self.k) > 0:
            # Iterate through the arrays and print in the specified format
            for i_val, j_val, k_val in zip(self.i, self.j, self.k):
                print(f"{i_val}, {j_val}, {k_val}")
        else:
            print("No data to print.")

    def convert_coords(self):

        if len(self.point_objects) > 0:
            self.point_objects[2].reverse_order()
            self.point_objects[3].reverse_order()
        else:
            print("No PointObject instances to convert.")
            return

        for points in self.point_objects:
            points.translate_to_origin(0)

            rotation_matrix = points.rotation_matrix(points.find_rz2(1), 'z')
            points.rotate(rotation_matrix)

            rotation_matrix = points.rotation_matrix(points.find_rx2(1), 'x')
            points.rotate(rotation_matrix)

            #nextBend = points.find_next_bend(0)
            rotation_matrix = points.rotation_matrix(points.find_ry2(2), 'y')
            points.rotate(rotation_matrix)

        rotation_matrix = points.rotation_matrix(math.pi, 'y')

        self.point_objects[1].rotate(rotation_matrix)
        self.point_objects[3].rotate(rotation_matrix)

        # After the conversion, update the GUI asynchronously
        self.collision_check()

        self.update_gui()
        # self.root.after(10, self.update_gui)

    def collision_check(self):
        # to be implemented
        # should define a collision rectangle using 8 points
        # Return length 4 boolean array with true if the coordinate system has a collision and false if not
        pass

    def plot_3d(self, point_object, title):

        mlab.figure(bgcolor=(1, 1, 1), fgcolor=(0, 0, 0), size=(640, 480))

        # Draw axes starting from the origin
        # X axis is red, Y axis is green, Z axis is blue
        origin = [0, 0, 0]
        axes_length = max(max(point_object.X), max(point_object.Y), max(point_object.Z))
        mlab.plot3d([origin[0], axes_length], [origin[1], origin[1]], [origin[2], origin[2]], color=(1, 0, 0), tube_radius=0.2, line_width=0.2)
        mlab.plot3d([origin[0], origin[0]], [origin[1], axes_length], [origin[2], origin[2]], color=(0, 1, 0), tube_radius=0.2, line_width=0.2)
        mlab.plot3d([origin[0], origin[0]], [origin[1], origin[1]], [origin[2], axes_length], color=(0, 0, 1), tube_radius=0.2, line_width=0.2)

        # Plot larger points as spheres
        mlab.points3d(point_object.X, point_object.Y, point_object.Z, color=(0, 0, 1), mode='sphere', scale_factor=1.5)

        # Draw lines between points
        for i in range(len(point_object.X) - 1):
            x = [point_object.X[i], point_object.X[i + 1]]
            y = [point_object.Y[i], point_object.Y[i + 1]]
            z = [point_object.Z[i], point_object.Z[i + 1]]
            mlab.plot3d(x, y, z, color=(0, 0, 1), tube_radius=.75)

        # Set title font size to 14
        # mlab.title(title, height=0.04)

        mlab.show()

    def calculate_bends(self):

        for points in self.point_objects:
            points.find_bends()

        # calculator = BendCalculator(self.point_objects)
        # bends = calculator.find_bends()
    def update_gui(self):
        # Update GUI elements here if necessary
        print("Coordinates Converted")

        # Generate 3D plots for each PointObject instance
        for idx, point_object in enumerate(self.point_objects):
            self.plot_3d(point_object, f'PointObject {idx + 1}')
            print(f"PointObject {idx + 1} coordinates:")
            point_object.print_contents()
            print()  # Add an empty line for better readability between PointObjects


if __name__ == "__main__":
    window = Tk()
    window.title('Wire Bender SW')
    window.geometry("700x500")
    window.config(background="white")
    gui = GUI(window)

    # Create a 'Print CSV' button and associate it with the print_csv method
    button_print_csv = Button(window, text="Print CSV", command=gui.print_csv)
    button_print_csv.grid(column=1, row=3)

    button_perform_operations = Button(window, text="Convert Coordinate System", command=gui.convert_coords)
    button_perform_operations.grid(column=1, row=4)

    window.mainloop()

