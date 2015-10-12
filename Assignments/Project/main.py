# TODO: Add the map (select subsection of nasa map based on longitude & lattitude), color & scale points, fetch from web using urlib (http://webservices.rm.ingv.it/fdsnws/event/1/query?starttime=2015-10-04+00%3A00%3A00&endtime=2015-10-11+23%3A59%3A59&minmag=2&maxmag=10&minlat=35&maxlat=48&minlon=6&maxlon=19&minversion=100&orderby=time-asc&format=text&limit=4000)

from vtk import *
#needed to determine the path to the source files
from os.path import dirname, realpath, join

from ReadPointsCSV import readPoints

def get_binary_relative_file(filepath):
    basedir = dirname(realpath(__file__)) #Get the directory of the .py file, courtesy of http://stackoverflow.com/a/5137509/4455880
    return join(basedir, filepath)

class KeyboardInterface(object):
    """Keyboard interface.

    Provides a simple keyboard interface for interaction. You may
    extend this interface with keyboard shortcuts for manipulating the
    molecule visualization.

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

# Load the earthquake data
points, point_strength, point_time, = readPoints("events3.csv")
min_strength, max_strength = point_strength.GetRange()
min_time, max_time = point_time.GetRange()  # in seconds

# Assign unique names to the scalar arrays
point_strength.SetName("strength")
point_time.SetName("time")

# Create a vtkPolyData object from the earthquake data and specify
# that "strength" should be the active scalar array
points_polydata = vtk.vtkPolyData()
points_polydata.SetPoints(points)
points_polydata.GetPointData().AddArray(point_strength)
points_polydata.GetPointData().AddArray(point_time)
points_polydata.GetPointData().SetActiveScalars("strength")

sphere_source = vtkSphereSource()

glyph = vtkGlyph3D();
glyph.SetSourceConnection(sphere_source.GetOutputPort());
glyph.SetInput(points_polydata)
glyph.SetColorModeToColorByScalar()
glyph.Update()

mapper = vtkPolyDataMapper()
mapper.SetInputConnection(glyph.GetOutputPort())

actor = vtkActor()
actor.SetMapper(mapper)

outline = vtkOutlineFilter()
outline.SetInput(points_polydata)
mapper_outline = vtkPolyDataMapper()
mapper_outline.SetInputConnection(outline.GetOutputPort())

actor_outline = vtkActor()
actor_outline.SetMapper(mapper_outline)

# Create a renderer and add the actors to it
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.2, 0.2, 0.2)
renderer.AddActor(actor)
renderer.AddActor(actor_outline)

render_window = vtk.vtkRenderWindow()
render_window.SetWindowName("earthquake")
render_window.SetSize(500, 500)
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
