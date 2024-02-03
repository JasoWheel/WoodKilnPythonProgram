# WoodKilnPythonProgram
A Python program on a Rasperry Pi and an Arduino Sketch to gather data from sensors and control fans and servo motors on a custom solar heated wood drying kiln.

The kiln is a 4' x 10' box with a clear roof to allow sunshine in and trap the heat. Inside is a circulation fan to push hot air though the wood stack, and linear actuators to open and close vent doors. There are temperature and humitity sensors inside and out; a light sensor, and magnetic switches to signal when the vent doors are open/closed. -- The Arduino periodically collects sensor data then creates and sends an ASCII string via the serial port to the Raspberry Pi. -- The Python progam stores, then uses the Arduino and other data it collects to determine if changes need to be made to the kiln fans and vents, then sends signals via it's I/O ports to make those changes. 
 
The .command file is a matplotlib/tkinter/numpy program to run on an external computer that takes data from .csv files created by the Python program and creates graphs.

A simple web page with more info, pictures and a video @ https://codepen.io/jasowheel/full/PdGwOw.
