# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import numpy as np
from scipy.optimize import fsolve

# these are all parameters that a user can change
wireDiameter = 3
offset = 0.8
pinPos = 16.5
bendAngle = 90


bendPin = 6
bendAngle = bendAngle * np.pi / 180

x0 = (2.5 + wireDiameter) * np.sin(bendAngle) + offset
y0 = (2.5 + wireDiameter) * np.cos(bendAngle) - (2.5 + wireDiameter/2)
print("x0:  ", x0)
print("y0:  ", y0)
slope = np.tan(bendAngle) * -1
print("slope: ", slope)

# wire line equation will take the form of ax + by + c = 0
# the wire slope is a
# b will be -1

c = y0 - slope * x0
print("c:  ", c)

a = slope
b = -1

def func(x):
    return [np.absolute(a*x[0] + b*x[1] + c) / np.sqrt(a**2 + b**2) - bendPin/2,
            np.sqrt(x[0]**2 + x[1]**2) - pinPos]

root = fsolve(func, [x0,y0])
print("solution: ", root)

motorAngle = np.arctan(root[1] / root[0]) * 180 / np.pi
print("motor angle: ", motorAngle)

