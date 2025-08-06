# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 19:51:16 2025

@author: Dan
"""

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
        fig, ax = plt.subplots()
        self.fig = fig
        self.ax = ax
        self.dragged_junction = None
        for j in self.junctions.values():
            j.draw(ax)

        for r in self.runs:
            r.draw(ax)

        fig.canvas.mpl_connect('button_press_event', self.on_press)
        fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        fig.canvas.mpl_connect('button_release_event', self.on_release)
        plt.axis('equal')
        plt.show()

    def redraw(self):
        if not hasattr(self, 'ax'):
            return  # Cannot redraw before draw() is called

        self.ax.clear()  # Clear previous visuals

        # Redraw all junctions and connections
        for j in self.junctions.values():
            j.draw(self.ax)

        for r in self.runs:
            r.calculateCurve()
            r.draw(self.ax)

        self.ax.axis('equal')
        self.fig.canvas.draw_idle()

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        for j in self.junctions.values():
            if j.nub_artist.contains(event)[0]:
                self.dragged_junction = j
                self.offset = j.loc - np.array([event.xdata, event.ydata])
                return

    def on_motion(self, event):
        if not self.dragged_junction or event.inaxes != self.ax:
            return
        new_pos = np.array([event.xdata, event.ydata]) + self.offset
        self.dragged_junction.update_position(new_pos)
        # update all the curves
        self.redraw()
        self.fig.canvas.draw_idle()

    def on_release(self, event):
        self.dragged_junction = None

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
        self.cost = 0

    def draw(self, ax):
        self.calculateCurve()
        ax.plot(self.curve[:, 0], self.curve[:, 1], self.color)

    def rescale(self, scale):
        plt.cla()
        self.scale = scale
        self.draw()

    def calculateCurve(self):
        self.curve = bezier_cubic(self.start,
                                  self.start + self.startGradient * self.scale,
                                  self.end + self.endGradient * self.scale,
                                  self.end)


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
        self.nub_artist = None  # Will be set during draw

    def get_points(self):
        self.r = rotation_matrix(self.direction)
        self.leftEndpoint = self.loc + np.array([self.flipped * -0.5, 1]) @ self.r
        self.rightEndpoint = self.loc + np.array([self.flipped * 0.5, 1]) @ self.r
        self.startGradient = np.array([0, -0.707]) @ self.r  # note the start gradient is pointing away from the root
        self.leftGradient = np.array([self.flipped * -0.5, 0.5]) @ self.r
        self.rightGradient = np.array([self.flipped * 0.5, 0.5]) @ self.r
        self.endpoints['left'] = self.leftEndpoint
        self.endpoints['right'] = self.rightEndpoint
        self.endpoints['root'] = self.loc
        self.gradients['left'] = self.leftGradient
        self.gradients['right'] = self.rightGradient
        self.gradients['root'] = self.startGradient

    def update_position(self, new_pos):
        self.loc = new_pos
        if self.nub_artist:
            dx, dy = [0, 0.5]@self.r
            self.nub_artist.set_data(new_pos[0] + dx, new_pos[1] + dy)
        self.get_points()

    def swap(self):
        self.flipped = -1 * self.flipped
        self.get_points()

    def calculateCurves(self):
        self.leftCurve = bezier_cubic(self.loc,
                                      self.loc - self.startGradient * self.scale,  # note, bezier gradient rule for startGradient is reversed here to converge at the root
                                      self.leftEndpoint - self.leftGradient * self.scale,
                                      self.leftEndpoint)

        self.rightCurve = bezier_cubic(self.loc,
                                       self.loc - self.startGradient * self.scale,  # note, bezier gradient rule for startGradient is reversed here to converge at the root
                                       self.rightEndpoint - self.rightGradient * self.scale,
                                       self.rightEndpoint)

    def draw(self, ax):
        self.calculateCurves()
        ax.plot(self.leftCurve[:, 0], self.leftCurve[:, 1], self.color)
        ax.plot(self.rightCurve[:, 0], self.rightCurve[:, 1], self.color, linestyle='--')

        # plot nub
        x, y = self.loc
        dx, dy = [0, 0.5]@self.r
        self.nub_artist = ax.plot(x+dx, y+dy, 'o', markersize=10, picker=True)[0]
        ax.text(*self.loc, self.name)


if __name__ == "__main__":

    plt.close('all')
    config = {"A": ["j1.left", "j2.right"],
              "B": ["j1.right", "j2.root"],
              "C": ["j1.root", "j2.left"]}

    # two reversing loops
    # config = {"A": ["j1.left", "j1.right"],
    #           "B": ["j2.root", "j1.root"],
    #           "C": ["j2.right", "j2.left"]}

    T = Track(config)
    T.draw()
