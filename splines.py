# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 19:51:16 2025

@author: Dan
"""

import numpy as np
import matplotlib.pyplot as plt
import random


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
            self.runs.append(Run(
                start_junction=self.junctions[startJunctionName],
                start_port=startJunctionNode,
                end_junction=self.junctions[endJunctionName],
                end_port=endJunctionNode,
                name=k,
                scale=self.runScale
            ))

    def draw(self):
        fig, ax = plt.subplots()
        self.fig = fig
        self.ax = ax
        self.dragged_junction = None
        self.angled_junction = None
        for j in self.junctions.values():
            j.draw(ax)

        for r in self.runs:
            r.draw(ax)

        fig.canvas.mpl_connect('button_press_event', self.on_press)
        fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        fig.canvas.mpl_connect('button_release_event', self.on_release)
        fig.canvas.mpl_connect('scroll_event', self.on_scroll)

        ax.set_title('Blue circles = move, Black circles=rotate \n Pink Squares=flip junction, scroll=tighten/loosen curves')

        ax.axis('equal')
        fig.show()

    def redraw(self):
        if not hasattr(self, 'ax'):
            return  # Cannot redraw before draw() is called

        self.ax.clear()  # Clear previous visuals

        self.ax.set_title('Blue circles = move, Black circles=rotate \n Pink Squares=flip junction, scroll=tighten/loosen curves')

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
            # Check for translation nub
            if j.nub_artist.contains(event)[0]:
                self.dragged_junction = j
                self.offset = j.loc - np.array([event.xdata, event.ydata])
                return

            # Check for rotation nub
            elif j.rot_artist.contains(event)[0]:
                self.angled_junction = j
                self.center = j.loc
                vec = np.array([event.xdata, event.ydata]) - self.center
                self.initial_angle = np.arctan2(vec[1], vec[0])
                self.initial_direction = j.direction
                return

            elif j.swap_artist.contains(event)[0]:
                j.swap()
                self.redraw()
                self.fig.canvas.draw_idle()

    def on_motion(self, event):
        if event.inaxes != self.ax:
            return

        if self.dragged_junction:
            # Handle dragging movement
            new_pos = np.array([event.xdata, event.ydata]) + self.offset
            self.dragged_junction.update_position(new_pos)
            self.redraw()
            self.fig.canvas.draw_idle()

        elif self.angled_junction:
            # Handle rotation
            vec = np.array([event.xdata, event.ydata]) - self.center
            current_angle = np.arctan2(vec[1], vec[0])
            delta_angle = np.rad2deg(self.initial_angle - current_angle)
            self.angled_junction.update_rotation(self.initial_direction + delta_angle)
            self.redraw()
            self.fig.canvas.draw_idle()

    def on_release(self, event):
        self.dragged_junction = None
        self.angled_junction = None

    def on_scroll(self, event):
        scale_step = 0.1
        if event.step > 0:
            self.runScale *= 1 + scale_step
        else:
            self.runScale *= 1 - scale_step
        self.rescale(self.runScale)
        self.redraw()
        self.fig.canvas.draw_idle()

    def rescale(self, scale):
        self.runScale = scale
        for r in self.runs:
            r.rescale(scale, self.ax)

    def traverse(self, log=False):
        """Traverse the track to see if we get stuck in a loop

        There are always two phases to each iteration:
            - 1. traverse from one end of a junction to another
            - 2. traverse from a node of one junction to a node of another via a run

        For 1, there are two options; starting at "left" or "right"
        and ending up at "root", or starting at the root and making a decision.

        For 2, there are no choices, the endpoint is governed
        fully by the run structure

        Returns True if we don't get stuck
        Returns False if we get stuck

        """
        stuck = False
        decisionCount = 0
        decisionLog = {}  # storage for whether to go left or right at a junction
        dCountLog = {}  # storage for decision count while entering
        keepLooking = True

        # 10 Start at the root of a random junction in the Track
        currentJunctionName = random.choice(list(self.junctions.keys()))
        currentNode = 'root'

        while keepLooking:
            if log:
                print(f'Current position: {currentJunctionName}.{currentNode}')
            # phase 1, go from one end of a junction to another
            if currentNode == 'root':

                # if we have turned left and right at all the junctions, then we are done
                if set(decisionLog.keys()) == set(T.junctions):
                    if np.all([v >= 2 for v in decisionLog.values()]):
                        keepLooking = False
                        continue

                # determine whether to go left or right from the decision log
                # if we have not travelled to this junction yet, go left (0)
                decisionValue = decisionLog.get(currentJunctionName, 0)
                if decisionValue == 0:
                    if log:
                        print(f"I haven't been at {currentJunctionName} before, going left")
                    currentNode = 'left'  # travel to the left outlet
                    decisionCount += 1
                    decisionLog[currentJunctionName] = 1
                elif decisionValue == 1:
                    if log:
                        print(f"I've turned left at {currentJunctionName} before, going right")
                    currentNode = 'right'  # travel to the right outlet
                    decisionCount += 1
                    decisionLog[currentJunctionName] = 2
                else:
                    currentNode = random.choice(['left', 'right'])
                    if log:
                        print(f"I've been to {currentJunctionName} twice before, picking {currentNode} randomly")
                    decisionCount += 1
                    decisionLog[currentJunctionName] += 1
            else:  # currentNode is 'left' or 'right', i.e. we have no choice
                if currentJunctionName in dCountLog.keys():
                    if decisionCount == dCountLog[currentJunctionName]:
                        # we haven't made any other decisions since we were last here
                        if log:
                            print('we got stuck')
                        stuck = True
                        keepLooking = False
                        continue
                    else:
                        # store the current decision count in the dCountLog
                        dCountLog[currentJunctionName] = decisionCount
                else:
                    dCountLog[currentJunctionName] = decisionCount

                # so we exit at the root of this junction
                currentNode = 'root'

            # phase 2 travel to the next junction
            # find our starting point in the runs structure
            if log:
                print(f'Current position: {currentJunctionName}.{currentNode}')
                print(f'Decision Log: {decisionLog}')
            for r in self.runs:
                if r.start_junction.name == currentJunctionName and r.start_port == currentNode:
                    # travel to the end
                    currentJunctionName = r.end_junction.name
                    currentNode = r.end_port
                    break
                elif r.end_junction.name == currentJunctionName and r.end_port == currentNode:
                    # travel to the start
                    currentJunctionName = r.start_junction.name
                    currentNode = r.start_port
                    break
            else:
                raise ValueError('Could not find a node to travel to next')

        if stuck:
            return False
        else:
            return True

    def findLoops(self, log=False):
        """Check the runs structure for loops. 

        Returns False if it's possible to get stuck in a loop'
        Returns True if it's a good structure (same as self.traverse)


        If it's ever possible to get back to the starting point without 
        making any decisions, i.e. entering a left or right node and exiting 
        a root node, then we have the first kind of problem (a loop)

        To find a loop like this, we need to exit from all the junctions' 
        root nodes. The current starting node is "j"
        - If the root node we are exiting is linked to 
          another root node, we have a decision, so we don't have a 1st 
          order loop
        - If the root node we are exiting is linked to a left or right node,
          exit via that root node and follow the path around.
              - If we get back to j without ever making a decision, this is a 
              problem. 

        It may be possible to have higher order loops, let's cover this later


        """

        # find all first order loops explicitly
        foundLoop = False
        for j in self.junctions.keys():  # starting from each junction's root node
            if log:
                print(f'Starting at junction {j}.root')
            next_junction = j
            loop_length = 0
            while True:
                # find where you end up when you exit this node
                # do this by scanning the runs structure for j.root,
                # and naming the end port
                if log:
                    print(f'Scanning the runs structure for {next_junction}.root')
                for r in self.runs:
                    skipFlag = False
                    if log:
                        print(f'current run is {r}')
                    if r.start_junction.name == next_junction and r.start_port == "root":
                        if log:
                            print(f'found {next_junction}.root at the start')
                        next_junction = r.end_junction
                        # if by exiting this port we hit a root node, we
                        # have a decision to make, so a journey leaving this
                        # junction in this direction is not part of a loop
                        if r.end_port == "root":
                            skipFlag = True
                        # whether we end up going into the left or right node
                        # of the next junction is immaterial, both converge at
                        # the root of the next junction.
                    # repeat the equivalent logic but the other way around
                    elif r.end_junction.name == next_junction and r.end_port == "root":
                        if log:
                            print(f'found {next_junction}.root at the end')
                        next_junction = r.start_junction
                        if r.start_port == "root":
                            skipFlag = True
                print(f'next junction = {next_junction}')
                loop_length += 1
                if skipFlag:
                    break  # out of the while loop, because root to root was found
                if next_junction == j and loop_length <= len(self.junctions):
                    print('Found a loop')
                    return False  # we have found a loop
                if loop_length > len(self.junctions):
                    break
        return True


class Run():
    # a Run has a start and end point and start and end gradients
    # a Run can also calculate its energy, and draw itself
    def __init__(self, start_junction, start_port, end_junction, end_port, name="", scale=0.5):
        self.start_junction = start_junction
        self.start_port = start_port
        self.end_junction = end_junction
        self.end_port = end_port
        self.scale = scale
        self.name = name
        self.color = 'b'
        self.cost = 0

    def draw(self, ax):
        self.calculateCurve()
        ax.plot(self.curve[:, 0], self.curve[:, 1], self.color)

    def rescale(self, scale, ax):
        self.scale = scale
        self.draw(ax)

    def calculateCurve(self):
        start = self.start_junction.endpoints[self.start_port]
        end = self.end_junction.endpoints[self.end_port]
        startGradient = self.start_junction.gradients[self.start_port]
        endGradient = self.end_junction.gradients[self.end_port]

        self.curve = bezier_cubic(start,
                                  start + startGradient * self.scale,
                                  end + endGradient * self.scale,
                                  end)

    def __repr__(self):
        return f"{self.start_junction.name}.{self.start_port} --> {self.end_junction.name}.{self.end_port}"


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
        self.swapped = 1  # or -1
        self.endpoints = {}
        self.gradients = {}
        self.get_points()
        self.nub_artist = None  # Will be set during draw
        self.rot_artist = None
        self.swap_artist = None

    def get_points(self):
        self.r = rotation_matrix(self.direction)
        self.leftEndpoint = self.loc + np.array([self.swapped * -0.5, 1]) @ self.r
        self.rightEndpoint = self.loc + np.array([self.swapped * 0.5, 1]) @ self.r
        self.startGradient = np.array([0, -0.707]) @ self.r  # note the start gradient is pointing away from the root
        self.leftGradient = np.array([self.swapped * -0.5, 0.5]) @ self.r
        self.rightGradient = np.array([self.swapped * 0.5, 0.5]) @ self.r
        self.endpoints['left'] = self.leftEndpoint
        self.endpoints['right'] = self.rightEndpoint
        self.endpoints['root'] = self.loc
        self.gradients['left'] = self.leftGradient
        self.gradients['right'] = self.rightGradient
        self.gradients['root'] = self.startGradient

    def update_position(self, new_pos):
        self.loc = new_pos
        if self.nub_artist:
            dx, dy = [0, 0.5] @ self.r
            self.nub_artist.set_data(new_pos[0] + dx, new_pos[1] + dy)
        self.get_points()

    def update_rotation(self, new_direction):
        self.direction = new_direction % 360
        self.get_points()

    def swap(self):
        self.swapped = -1 * self.swapped
        self.get_points()

    def calculateCurves(self):
        self.leftCurve = bezier_cubic(self.loc,
                                      # note, bezier gradient rule for startGradient is reversed here to converge at the root
                                      self.loc - self.startGradient * self.scale,
                                      self.leftEndpoint - self.leftGradient * self.scale,
                                      self.leftEndpoint)

        self.rightCurve = bezier_cubic(self.loc,
                                       # note, bezier gradient rule for startGradient is reversed here to converge at the root
                                       self.loc - self.startGradient * self.scale,
                                       self.rightEndpoint - self.rightGradient * self.scale,
                                       self.rightEndpoint)

    def draw(self, ax):
        self.calculateCurves()
        ax.plot(self.leftCurve[:, 0], self.leftCurve[:, 1], self.color)
        ax.plot(self.rightCurve[:, 0], self.rightCurve[:, 1], self.color, linestyle='--')

        # plot nub
        x, y = self.loc
        dx, dy = [0, 0.5] @ self.r
        self.nub_artist = ax.plot(x + dx, y + dy, 'bo', markersize=10, picker=True)[0]
        self.rot_artist = ax.plot(x + 1.3 * dx, y + 1.3 * dy, 'ko', markersize=7, picker=True)[0]
        self.swap_artist = ax.plot(x + 0.7 * dx, y + 0.7 * dy, 'ms', markersize=7, picker=True)[0]
        ax.text(*self.loc, self.name)

    def __repr__(self):
        return self.name


if __name__ == "__main__":

    plt.close('all')

    print('Config 1 - gets stuck, should return False, bad layout')
    config = {"A": ["j1.left", "j2.right"],
              "B": ["j1.right", "j2.root"],
              "C": ["j1.root", "j2.left"]}
    T = Track(config)
    T.draw()
    print(T.findLoops(log=True))
    # print(T.traverse())

    print('Config 2 - two reversing loops, good layout, should return True')
    config = {"A": ["j1.left", "j1.right"],
              "B": ["j2.root", "j1.root"],
              "C": ["j2.right", "j2.left"]}
    T = Track(config)
    T.draw()
    # print(T.findLoops())
    # print(T.traverse())

    # gets stuck [j3 root, j2 left, j2 root, j1 right, j1 root, j1 root, j3 left, j3 root]
    config = {"A": ["j1.left", "j2.right"],
              "B": ["j1.right", "j2.root"],
              "C": ["j1.root", "j3.left"],
              "D": ["j2.left", "j3.root"],
              "E": ["j3.right", "j4.root"],
              "F": ["j4.left", "j4.right"]}
    T = Track(config)
    T.draw()
    # print(T.findLoops())
    print(T.traverse())

    # if travelling from j1.root to j3.right, can always alternate between
    # two loops by choosing at j2 but can't ever enter j4
    # possibly use the decisionLog to tell that if we have made
    # more than 2 decisions at a junction, but can't decide
    # at any other junctions, then we are stuck in a double loop?
    # config = {"A": ["j1.left", "j4.root"],
    #           "B": ["j3.root", "j2.root"],
    #           "C": ["j1.root", "j3.left"],
    #           "D": ["j2.left", "j1.right"],
    #           "E": ["j3.right", "j2.right"],
    #           "F": ["j4.left", "j4.right"]}

    # another double loop
    # config = {"A": ["j1.left", "j4.root"],
    #           "B": ["j3.root", "j2.root"],
    #           "C": ["j1.root", "j3.left"],
    #           "D": ["j2.left", "j1.right"],
    #           "E": ["j3.right", "j4.right"],
    #           "F": ["j4.left", "j2.right"]}

    # good one!
    # config = {"A": ["j2.left", "j4.root"],
    #           "B": ["j3.root", "j2.root"],
    #           "C": ["j1.root", "j3.left"],
    #           "D": ["j1.left", "j1.right"],
    #           "E": ["j3.right", "j4.right"],
    #           "F": ["j4.left", "j2.right"]}

    # This is a counterexample to the root-to-root hypothesis.
    # Although I can visit all edges, I can't do so in both directions
    # so this is a bad layout
    config = {'A': ["j1.left", "j2.left"],
              'B': ["j1.right", "j2.right"],
              'C': ["j1.root", "j2.root"]}

    T = Track(config)
    # print(T.findLoops())
    # print(T.traverse())
    T.draw()
