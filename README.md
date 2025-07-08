# trains
Investigations into the design of good toy train layouts.

My definition of a *good* toy train layout is one where: 

"A train starting at any point on the track, facing in either direction, can make a journey where it travels on all sections of track in both directions, and returns to its starting point, facing the same direction it started."

This necessitates that the track has sets of points that let the train take different paths (otherwise it would not be able to turn around). In general a track must have an even number of sets of points to avoid dead ends. 

The simplest "good" layout is a straight piece of track with a reversing loop at each end: 

![image](https://github.com/user-attachments/assets/a65c3a94-f918-45e5-ae47-74a99135e427)

The train completes one circuit as pictured, taking the left fork at each set of points, then can complete another similar loop taking the right fork (therefore traversing all sections of track in both directions). 

The following is an example of a "bad" layout. When travelling anticlockwise towards junction A (green arrow), the train can take either direction, but if the train takes the branch across the middle of the layout, it gets stuck in a clockwise loop, unable to make any more decisions. 

![image](https://github.com/user-attachments/assets/72f0aa19-3278-4a5c-bab6-0821f52656db)

If a reversing loop (CD) is added anywhere in the layout, the layout is solved again, and it's no longer possible for a train to get stuck in a loop

![image](https://github.com/user-attachments/assets/7e4f3ff0-d3b7-4128-90e3-00ab2e4abdb0)

My aims are: 

- to see if this problem can be solved in general
- to discover if there are any easy-to-learn rules (e.g. like counting sets of points in a given direction) that make it possible to check if a layout is good without having to trace out all possible paths 
- to discover an algorithm to turn a bad layout into a good layout 
