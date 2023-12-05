"""
This class contains the methods for generating a G-Code file from a point_object instance.
The constructor takes a point_object and copies all important instance variables for G-Code purposes

Anderson Boyer
"""
class BenderGCode:

    def __init__(self, point_object):

        self.L = point_object.L
        self.R = point_object.R
        self.A = point_object.A
        self.MA = point_object.MA
        self.pin_pos = point_object.pin_pos

    def generate_gcode(self):
        """
        Generate G-code based on LRA data and save it to a file.

        Parameters:
        - self
        """

        gcode = []
        comment = []

        gcode.append("%")
        comment.append("")

        gcode.append(f'; For use with {round(self.pin_pos, 1)} mm pin only')
        comment.append("")
        gcode.append("")
        comment.append("")
        gcode.append("")
        comment.append("")

        if self.pin_pos > 12.1:
            gcode.append("M98 P\"not12mm.g\"")
            comment.append("")

        bender_position = 1

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
                gcode.append(f"G1 X{round(current_x, 2)}")
                comment.append(f';  Extrude wire {round(self.L[i], 2)} mm')

            if (len(self.R) > 0) & (len(self.A) > 0):
                # Check R value threshold
                if abs(self.R[i]) > 0.01:  # Adjust the threshold as needed
                    # Add G1 command for Y movement
                    current_y += self.R[i]
                    gcode[-1] = gcode[-1] + f" Y{round(current_y, 2)}"
                    # gcode.append(f"G1 Y{round(current_y, 2)}")
                    comment[-1] = comment[-1] + f' and rotate wire {round(self.R[i], 2)} degrees'
                    # comment.append(f';  Rotate wire {round(self.R[i], 2)} degrees')

                # previous bend was negative, need to duck and move to positive position
                if (self.A[i] > .02) & (bender_position == 1):
                    gcode.append("M106 P0 S1.0")
                    comment.append(f';  Ducking pin for positive bend')
                    gcode.append("G0 Z-30")
                    comment.append(f'')
                    gcode.append("M106 P0 S0")
                    comment.append(f'')
                    bender_position = -1
                elif (self.A[i] < -.02) & (bender_position == -1):
                    gcode.append("M106 P0 S1.0")
                    comment.append(f';  Ducking pin for negative bend')
                    gcode.append("G0 Z30")
                    comment.append(f'')
                    gcode.append("M106 P0 S0")
                    comment.append(f'')
                    bender_position = 1

                # Check A value threshold
                if abs(self.A[i]) > 0.02:  # Adjust the threshold as needed
                    gcode.append(f"G1 Z{round(self.MA[i], 2)}")
                    comment.append(f';  Setting motor angle to {round(self.MA[i], 2)} degrees for {round(self.A[i], 2)}'
                                   f' degree desired bend')
                    if self.A[i] < 0:
                        gcode.append("G0 Z30")
                        comment.append(f';  Return pin to positive position')
                        bender_position = 1
                    elif self.A[i] > 0:
                        gcode.append("G0 Z-30")
                        comment.append(f';  Return pin to negative position')
                        bender_position = -1

        gcode.append("%")
        comment.append(0)
        return [gcode, comment]
