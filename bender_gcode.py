class benderGCode:
    # References:
    # https://howtomechatronics.com/tutorials/g-code-explained-list-of-most-important-g-code-commands/
    # https://www.cnccookbook.com/g-code-basics-program-format-structure-blocks/

    def __init__(self, point_object):

        self.L = point_object.L
        self.R = point_object.R
        self.A = point_object.A

        self.command_dictionary = {
            "set to mm": "G21",
            "Global Coordinates": "G90",  # sets to absolute mode
            "End Program": "M30",
            "Home": "G28",
            "Feed": "G00 ",  # G00 commands movemente at max speed
            "Bend": "G01 ",  # G01 commands movement at speed set in fourth and final parameter
            "Rotate": "G00 "
        }

        self.bend_speed = "100"  # mm/min
        self.gcode_lines = []
        self.line_number = 0

    def generate_gcode(self):
        """
        Generate G-code based on LRA data and save it to a file.

        Parameters:
        - filename: The name of the G-code file to be saved.
        - bend_pin_location: The selected bend pin location (e.g., "6 mm", "10 mm", "14 mm").
        - material: The selected material (e.g., "spring steel", "stainless steel", "mild steel", "aluminum").
        - wire_diameter: The selected wire diameter (e.g., "0.5 mm", "0.75 mm", "1 mm", "1.5 mm", "2 mm").
        """

        gCode = []
        gCode.append("%")
        gCode.append("G1 Z30")

        benderPosition = 1


        # Initialize current X, Y, Z values
        current_x = 0.0
        current_y = 0.0

        # Iterate through LRA data and add G1 commands based on thresholds
        for i in range(len(self.L)):
            # Check L value threshold
            if abs(self.L[i]) > 0.01:  # Adjust the threshold as needed
                # Update current_x
                current_x += self.L[i]
                # Add G1 command for X movement
                gCode.append(f"G1 X{round(current_x, 2)}")

            # Check R value threshold
            if abs(self.R[i]) > 0.01:  # Adjust the threshold as needed
                # Add G1 command for Y movement
                current_y += self.R[i]
                gCode.append(f"G1 Y{round(current_y, 2)}")


            # previous bend was negative, need to duck and move to positive position
            if (i > 0) & ((self.A[i] > .02) & (benderPosition == 1)):
                gCode.append("M106 P0 S1.0")
                gCode.append("G1 Z30")
                gCode.append("M106 P0 S0")
                benderPosition = -1
            elif (i > 0) & ((self.A[i] < -.02) & (benderPosition == -1)):
                gCode.append("M106 P0 S1.0")
                gCode.append("G1 Z-30")
                gCode.append("M106 P0 S0")
                benderPosition = 1

            # Check A value threshold
            if abs(self.A[i]) > 0.02:  # Adjust the threshold as needed
                gCode.append(f"G1 Z{round(self.A[i], 2)}")
                if self.A[i] < 0:
                    gCode.append("G1 Z30")
                    benderPosition = 1
                elif self.A[i] > 0:
                    gCode.append("G1 Z-30")
                    benderPosition = -1

        gCode.append("%")
        return gCode


    # def add_gcode_line(self, line):
    #     line_number_string = "N"
    #     if (self.line_number < 10):
    #         line_number_string += "00"
    #     elif (self.line_number < 100):
    #         line_number_string += "0"
    #
    #     self.gcode_lines.append(line_number_string + str(self.line_number) + " " + line + "\n")
    #     self.line_number += 1

    # def write_gcode_lines(self):
    #     self.gcode_lines.append("%\n")
    #     self.gcode_lines.append("(Header)\n")
    #     self.gcode_lines.append("(End Header)\n\n")
    #     self.add_gcode_line(self.command_dictionary["set to mm"] + "\n")
    #     self.add_gcode_line(self.command_dictionary["Feed"] + "X20.0 " + "Y0.0 " + "Z0.0")
    #     self.add_gcode_line(self.command_dictionary["Bend"] + "X0.0 " + "Y0.0 " + "Z90.0 F" + self.bend_speed)
    #     self.add_gcode_line(self.command_dictionary["Feed"] + "X0.0 " + "Y30.0 " + "Z0.0")
    #     self.add_gcode_line(self.command_dictionary["End Program"])
    #     self.gcode_lines.append("%")

    # def write_to_file(self, filename):
    #     self.file = open(filename + ".gcode", "w")
    #     self.file.writelines(self.gcode_lines)
    #     self.file.close()