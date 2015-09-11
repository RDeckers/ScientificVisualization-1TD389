"""Isosurface extraction.

This script should extract and display isosurfaces of the probability
density of a hydrogen atom in a volume dataset.

You can run the script from the command line by typing
python isosurface.py

"""

from vtk import *

#needed to determine the path to the source files
from os.path import dirname, realpath, join

# Define a class for the keyboard interface
class KeyboardInterface(object):
    """Keyboard interface.

    Provides a simple keyboard interface for interaction. You should
    extend this interface with keyboard shortcuts for changing the
    isovalue interactively.

    """

    def __init__(self): #TODO: Read up op Python classes, move initialization into here, absorb an relevant variables.
        self.screenshot_counter = 0
        self.window2image_filter = None
        self.png_writer = None

    def keypress(self, obj, event):
        """This function captures keypress events and defines actions for
        keyboard shortcuts."""
        key = obj.GetKeySym()
        if key == "9":
            render_window.Render()
            self.window2image_filter.Modified()
            screenshot_filename = ("screenshot%02d.png" %
                                   (self.screenshot_counter))
            self.png_writer.SetFileName(screenshot_filename)
            self.png_writer.Write()
            print("Saved %s" % (screenshot_filename))
            self.screenshot_counter += 1
        elif key == "1":
            contour_filter.SetValue(0, 0.7)
            render_window.Render()
        elif key == "2":
            contour_filter.SetValue(0, 0.3)
            render_window.Render()


# Read the volume dataset
basedir = dirname(realpath(__file__)) #Get the directory of the .py file, courtesy of http://stackoverflow.com/a/5137509/4455880
filename = join(basedir, "hydrogen.vtk")
reader = vtk.vtkStructuredPointsReader()
reader.SetFileName(filename)
print("Reading volume dataset from " + filename + " ...")
reader.Update()  # executes the reader
print("Done!")

# Just for illustration, extract and print the dimensions of the
# volume. The string formatting used here is similar to the sprintf
# style in C.
width, height, depth = reader.GetOutput().GetDimensions()
print("Dimensions: %i %i %i" % (width, height, depth))

# Create an outline of the volume
outline = vtk.vtkOutlineFilter()
outline.SetInput(reader.GetOutput())
outline_mapper = vtk.vtkPolyDataMapper()
outline_mapper.SetInput(outline.GetOutput())
outline_actor = vtk.vtkActor()
outline_actor.SetMapper(outline_mapper)

# Define actor properties (color, shading, line width, etc)
outline_actor.GetProperty().SetColor(0.8, 0.8, 0.8)
outline_actor.GetProperty().SetLineWidth(2.0)

contour_filter = vtkContourFilter()
contour_filter.SetInputConnection(reader.GetOutputPort())
contour_filter.SetValue(0, 0.5)

surface_mapper = vtkPolyDataMapper()
surface_mapper.SetInputConnection(contour_filter.GetOutputPort())

surface_actor = vtkActor()
surface_actor.SetMapper(surface_mapper)


# Create a renderer and add the actors to it
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.2, 0.2, 0.2)
renderer.AddActor(outline_actor)
renderer.AddActor(surface_actor)

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.SetWindowName("Isosurface extraction")
render_window.SetSize(500, 500)
render_window.AddRenderer(renderer)

# Create an interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Create a window-to-image filter and a PNG writer that can be used
# for taking screenshots
window2image_filter = vtk.vtkWindowToImageFilter()
window2image_filter.SetInput(render_window)
png_writer = vtk.vtkPNGWriter()
png_writer.SetInput(window2image_filter.GetOutput())

# Set up the keyboard interface
keyboard_interface = KeyboardInterface()
keyboard_interface.window2image_filter = window2image_filter #TODO: Move these out of the way
keyboard_interface.png_writer = png_writer

# Connect the keyboard interface to the interactor
interactor.AddObserver("KeyPressEvent", keyboard_interface.keypress)

# Initialize the interactor and start the rendering loop
interactor.Initialize()
render_window.Render()
interactor.Start()
