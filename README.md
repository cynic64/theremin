# theremin

This is a collection of programs for doing fun things with a green-screen. It uses the opencv-python package to do all the image processing and works with python 3.8. It contains 5 runnable files which all take a video feed from the camera and transform it in some way.

## Files
`background_subtraction.py`: Takes a feed from the camera and replaces everything green with a predetermined background image (by default a picture of the Eiffel Tower). **A lot of the code is directly copied from some of the [OpenCV python examples](https://github.com/opencv/opencv/tree/master/samples/python)**.

`camshift.py`: Demonstrates the CAMshift object tracking algorithm and is also taken from the OpenCV samples repository: [camshift.py](https://github.com/opencv/opencv/blob/master/samples/python/camshift.py). After running it (`python3 camshift.py`), press S to open a 2nd window allowing you to select what to track by dragging a rectangle around an object. It doesn't work well on some background/object combinations as it is only meant to track white jackets on green background (see the "Purpose" section).

The reason background_subtraction and camshift are in this repository even though they are derivatives of the OpenCV samples is because they are used as libraries in some of the other, more interesting files, as described below.

`theremin_and_backsub.py`: Simulates a [theremin](https://en.wikipedia.org/wiki/Theremin) by tracking an object across the screen as well as doing a background swap. The farther right the object is on the video feed, the higher the pitch, and the higher the object on the screen, the higher the volume. Either mplayer (on Linux) or afplay (on Mac) are required to play the theremin sounds. It imports functions from theremin.py and background_subtraction.py.

`theremin.py`: A library with the theremin functionality that does the actual playing of sounds.

`camshift_drawing.py`: Like camshift, but draws a trail behind the object, letting you (for example) write out your name by moving a colorful ball in front of the screen. Mouse-1 toggles drawing, Mouse-2 swaps the brush color between green and blue.

## Purpose
I was asked to create some kind of demo for a huge green-screen my school had just bought, and theremin_and_backsub is that. Parents who were touring the new facility could put on a white lab coat and dance in front of the green screen. The white lab coat would be tracked and used to control a theremin. Jumping would produce a louder sound, while running left and right would change the pitch of the theremin. The background was also replaced, which was made easy by the contrast between the green-screen and the white lab coats. The other programs are smaller parts that theremin_and_backsub was built on top of.

## Running
You'll need python 3.8 and opencv-python:
```
pip3 install --user opencv-python
```
Then just cd to the directory you cloned into and run whichever file you want.
