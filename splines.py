# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 19:51:16 2025

@author: Dan
"""


# import matplotlib.pyplot as plt
# import numpy as np
# from scipy import interpolate


# nodes = np.array([[1, 2], [6, 15], [10, 6], [10, 3], [3, 7]])

# x = nodes[:, 0]
# y = nodes[:, 1]

# tck, u = interpolate.splprep([x, y], s=0)
# xnew, ynew = interpolate.splev(np.linspace(0, 1, 100), tck, der=0)

# plt.plot(x, y, 'o', xnew, ynew)
# plt.legend(['data', 'spline'])
# plt.axis([x.min() - 1, x.max() + 1, y.min() - 1, y.max() + 2])
# plt.show()

import numpy as np
import matplotlib.pyplot as plt


def rotation_matrix(theta):
    """Returns a 2D rotation matrix for angle theta (in degrees)."""
    return np.array([
        [np.cos(np.deg2rad(theta)), -np.sin(np.deg2rad(theta))],
        [np.sin(np.deg2rad(theta)),  np.cos(np.deg2rad(theta))]
    ])


def bezier_cubic(P0, P1, P2, P3, n=100):
    t = np.linspace(0, 1, n)[:, None]  # shape (100, 1)

    return (1 - t)**3 * P0 + \
        3 * (1 - t)**2 * t * P1 + \
        3 * (1 - t) * t**2 * P2 + \
        t**3 * P3


class Track():
    # a track contains some junctions and connections

    def __init__(self, junctionRules):
        # from the map of connections, connect all the junctions
        self.junctions = []
        self.runs = []
        junctionNames, runs = junctionRules.items()
        for name in junctionNames:
            # put a random junction down
            self.junctions.append(Junction(np.random.randn(2)*5, np.random.rand()*360, name))

        for
        # make all the runs from this junction
        for rule in junctionName
        self.runs.append()

    def draw(self):
        for j in self.junctions:
            j.draw()
            plt.axis('equal')


class Run():
    # a Run has a start and end point and start and end gradients
    # a Run can also calculate its energy, and draw itself
    def __init__(self, start, end, startGradient, endGradient):
        self.start = start
        self.end = end
        self.startGradient = startGradient
        self.endGradient = endGradient
        self.scale = 0.5
        self.color = 'b'

    def draw(self):
        curve = bezier_cubic(self.start,
                             self.start+self.startGradient*self.scale,
                             self.end-self.endGradient*self.scale,
                             self.end)

        plt.plot(curve[:, 0], curve[:, 1], self.color)


class Junction():
    # a junction has coordinates that define its root
    # and an angle that defines which direction it goes in
    def __init__(self, loc, direction, name):
        """
        Parameters
        ----------
        loc: np.array of float: [x,y]
            location of root 
        direction : scalar float in degrees 
            direction that the midpoint of the junction points 
        """
        self.loc = loc
        self.direction = direction
        self.scale = 0.5
        self.color = 'r'
        self.name = name
        self.flipped = 1  # or -1
        self.get_points()

    def get_points(self):
        r = rotation_matrix(self.direction)
        self.leftEndpoint = self.loc+np.array([self.flipped*-0.5, 1])@r
        self.rightEndpoint = self.loc+np.array([self.flipped*0.5, 1])@r
        self.startGradient = np.array([0, 0.707])@r
        self.leftGradient = np.array([-0.5, 0.5])@r
        self.rightGradient = np.array([0.5, 0.5])@r

    def swap(self):
        self.flipped = -1*self.flipped
        self.get_points()

    def draw(self):
        # plt.plot(*self.loc, 'kx')
        # plt.plot(*self.leftEndpoint, 'bx')
        # plt.plot(*self.rightEndpoint, 'rx')

        leftCurve = bezier_cubic(self.loc,
                                 self.loc+self.startGradient*self.scale,
                                 self.leftEndpoint-self.leftGradient*self.scale,
                                 self.leftEndpoint)

        rightCurve = bezier_cubic(self.loc,
                                  self.loc+self.startGradient*self.scale,
                                  self.rightEndpoint-self.rightGradient*self.scale,
                                  self.rightEndpoint)

        plt.plot(leftCurve[:, 0], leftCurve[:, 1], self.color)
        plt.plot(rightCurve[:, 0], rightCurve[:, 1], self.color)
        plt.text(*self.loc, self.name)


if __name__ == "__main__":

    junctionRules = {
        'j1': {'left': 'j2.right', 'right': 'j2.root'},
        'j2': {'right': 'j1.root'}
    }

    T = Track(junctionRules)
    T.draw()

    # plt.close('all')
    # j = Junction([1, 0], 45, 'j1')
    # j.draw()
    # plt.axis('equal')
    # k = Junction([-2, 1], 135, 'j2')
    # k.draw()
    # plt.axis('equal')

    # c = Run(k.leftEndpoint, j.loc, k.leftGradient, j.startGradient)
    # c.draw()
