# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 12:42:37 2025

@author: Dan
"""

# runs = {"A": ["j1.left", "j2.right"],
#         "B": ["j1.right", "j2.root"],
#         "C": ["j1.root", "j2.left"]}


# ported to splines.py
# # find all the junctions mentioned
# junctionNames = set()
# for k, v in runs.items():  # for each run
#     for end in v:  # for each connection termination
#         currentJunctionName = end.split('.')[0]
#         if currentJunctionName not in junctionNames:
#             # make a junction object with random coordinates
#             pass
#         else:
#             junctionNames.add(currentJunctionName)
#     # now that all the junctions associated with the current run have been created,
#     # make a run object from the current run
#     startJunctionName = v[0].split('.')[0]
#     startJunctionNode = v[0].split('.')[1]
#     endJunctionName = v[1].split('.')[0]
#     endJunctionNode = v[1].split('.')[1]
#     # runs.append(Run(Track.startJunctionName, Track.endJunctionName)) # or the junction obj itself?
#     # need to make a way of ID'ing junctions by name, maybe Track.junctions is a dict.


# after this function we should have a Track which has all connections made.

# traverse the track.

# 10 Start at the root of the first junction in the Track
# 20 We always have a decision in the first case:
#      Take the left path and remember that we have already exited from this junction
# 50 Use the runs structure to follow the track to the next junction node
# Did we enter at a root node?
#   YES - we have a decision. Increment the decision counter
#       if the decision counter is bigger than the number of junctions, exit, else continue
#       Have we been to this node before?
#         YES - Therefore we have previously exited via the left node, take the right path, goto 50
#         NO - Take the left path, goto 50
#   NO - Have we been here before?
#       YES - What was the decision counter last time we were here?
#           SAME AS LAST TIME? then there is a mandatory loop - exit
#           not the same? save decision counter here.
#       NO - goto 50
#
# decision counter? like, has the decision counter increased since we last arrived at this node
