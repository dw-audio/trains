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
        [np.sin(np.deg2rad(theta)), np.cos(np.deg2rad(theta))]
    ])


def bezier_cubic(P0, P1, P2, P3, n=100):
    t = np.linspace(0, 1, n)[:, None]  # shape (100, 1)

    return (1 - t)**3 * P0 + \
        3 * (1 - t)**2 * t * P1 + \
        3 * (1 - t) * t**2 * P2 + \
        t**3 * P3


class Track():
    # a track contains some junctions and connections

    def __init__(self, config):
        # from the config, connect all the junctions
        # config has the form of a dictionary with entries
        # {"name of run": ["<junction name>.<left|right|root>",
        #                  "<junction name>.<left|right|root>"]}

        self.junctions = {}  # keys = names, values = junction objects
        self.runs = []
        self.runScale = 0.5
        for k, v in config.items():  # for each run
            for end in v:  # for each connection termination
                currentJunctionName = end.split('.')[0]
                if currentJunctionName not in self.junctions.keys():
                    self.junctions[currentJunctionName] = Junction(np.random.randn(2) * 2,
                                                                   np.random.rand() * 360,
                                                                   currentJunctionName)
                else:
                    pass
            # now that all the junctions associated with the current run have been created,
            # make a run object from the current run
            startJunctionName = v[0].split('.')[0]
            startJunctionNode = v[0].split('.')[1]
            endJunctionName = v[1].split('.')[0]
            endJunctionNode = v[1].split('.')[1]
            self.runs.append(Run(self.junctions[startJunctionName].endpoints[startJunctionNode],
                                 self.junctions[endJunctionName].endpoints[endJunctionNode],
                                 self.junctions[startJunctionName].gradients[startJunctionNode],
                                 self.junctions[endJunctionName].gradients[endJunctionNode],
                                 k,
                                 self.runScale))

    def draw(self):
        for j in self.junctions.values():
            j.draw()
            plt.axis('equal')
        for r in self.runs:
            r.draw()

    def rescale(self, scale):
        for r in self.runs:
            r.rescale(scale)


class Run():
    # a Run has a start and end point and start and end gradients
    # a Run can also calculate its energy, and draw itself
    def __init__(self, start, end, startGradient, endGradient, name="", scale=0.5):
        self.start = start
        self.end = end
        self.startGradient = startGradient
        self.endGradient = endGradient
        self.scale = scale
        self.color = 'b'
        self.name = name

    def draw(self):
        curve = bezier_cubic(self.start,
                             self.start + self.startGradient * self.scale,
                             self.end + self.endGradient * self.scale,
                             self.end)

        plt.plot(curve[:, 0], curve[:, 1], self.color)

    def rescale(self, scale):
        plt.cla()
        self.scale = scale
        self.draw()


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
        self.endpoints = {}
        self.gradients = {}
        self.get_points()

    def get_points(self):
        r = rotation_matrix(self.direction)
        self.leftEndpoint = self.loc + np.array([self.flipped * -0.5, 1]) @ r
        self.rightEndpoint = self.loc + np.array([self.flipped * 0.5, 1]) @ r
        self.startGradient = np.array([0, -0.707]) @ r  # note the start gradient is pointing away from the root
        self.leftGradient = np.array([self.flipped * -0.5, 0.5]) @ r
        self.rightGradient = np.array([self.flipped * 0.5, 0.5]) @ r
        self.endpoints['left'] = self.leftEndpoint
        self.endpoints['right'] = self.rightEndpoint
        self.endpoints['root'] = self.loc
        self.gradients['left'] = self.leftGradient
        self.gradients['right'] = self.rightGradient
        self.gradients['root'] = self.startGradient

    def swap(self):
        self.flipped = -1 * self.flipped
        self.get_points()

    def draw(self):

        leftCurve = bezier_cubic(self.loc,
                                 self.loc - self.startGradient * self.scale,  # note, bezier gradient rule for startGradient is reversed here to converge at the root
                                 self.leftEndpoint - self.leftGradient * self.scale,
                                 self.leftEndpoint)

        rightCurve = bezier_cubic(self.loc,
                                  self.loc - self.startGradient * self.scale,  # note, bezier gradient rule for startGradient is reversed here to converge at the root
                                  self.rightEndpoint - self.rightGradient * self.scale,
                                  self.rightEndpoint)

        plt.plot(leftCurve[:, 0], leftCurve[:, 1], self.color)
        plt.plot(rightCurve[:, 0], rightCurve[:, 1], self.color, linestyle='--')
        plt.text(*self.loc, self.name)


if __name__ == "__main__":

    config = {"A": ["j1.left", "j2.right"],
              "B": ["j1.right", "j2.root"],
              "C": ["j1.root", "j2.left"]}

    # two reversing loops
    # config = {"A": ["j1.left", "j1.right"],
    #           "B": ["j2.root", "j1.root"],
    #           "C": ["j2.right", "j2.left"]}

    T = Track(config)
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
