"""Air currents.

This script should display a visualization of a vtkStructuredPoints
dataset containing the direction and speed of air currents over North
America.

You can run the script from the command line by typing
python wind.py

"""

import vtk

#needed to determine the path to the source files
from os.path import dirname, realpath, join


# Define a class for the keyboard interface
class KeyboardInterface(object):
    """Keyboard interface.

    Provides a simple keyboard interface for interaction. You may
    extend this interface with keyboard shortcuts for, e.g., moving
    the slice plane(s) or manipulating the streamline seedpoints.

    """

    def __init__(self):
        self.screenshot_counter = 0
        self.render_window = None
        self.window2image_filter = None
        self.png_writer = None
        # Add the extra attributes you need here...

    def keypress(self, obj, event):
        """This function captures keypress events and defines actions for
        keyboard shortcuts."""
        key = obj.GetKeySym()
        if key == "9":
            self.render_window.Render()
            self.window2image_filter.Modified()
            screenshot_filename = ("screenshot%02d.png" %
                                   (self.screenshot_counter))
            self.png_writer.SetFileName(screenshot_filename)
            self.png_writer.Write()
            print("Saved %s" % (screenshot_filename))
            self.screenshot_counter += 1
        # Add your keyboard shortcuts here. If you modify any of the
        # actors or change some other parts or properties of the
        # scene, don't forget to call the render window's Render()
        # function to update the rendering.
        # elif key == ...


# Read the dataset
reader = vtk.vtkStructuredPointsReader()
basedir = dirname(realpath(__file__)) #Get the directory of the .py file, courtesy of http://stackoverflow.com/a/5137509/4455880
reader.SetFileName(join(basedir, "wind.vtk"))
reader.Update()

#
#
# Add your code here...
#
#

# Create a renderer and add the actors to it
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.2, 0.2, 0.2)
# renderer.AddActor(...)

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.SetWindowName("Air currents")
render_window.SetSize(800, 600)
render_window.AddRenderer(renderer)

# Create an interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Create a window-to-image filter and a PNG writer that can be used
# to take screenshots
window2image_filter = vtk.vtkWindowToImageFilter()
window2image_filter.SetInput(render_window)
png_writer = vtk.vtkPNGWriter()
png_writer.SetInput(window2image_filter.GetOutput())

# Set up the keyboard interface
keyboard_interface = KeyboardInterface()
keyboard_interface.render_window = render_window
keyboard_interface.window2image_filter = window2image_filter
keyboard_interface.png_writer = png_writer

# Connect the keyboard interface to the interactor
interactor.AddObserver("KeyPressEvent", keyboard_interface.keypress)

# Initialize the interactor and start the rendering loop
interactor.Initialize()
render_window.Render()
interactor.Start()
