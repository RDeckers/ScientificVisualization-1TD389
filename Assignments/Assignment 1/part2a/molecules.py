"""Molecular dynamics.

This script should display the atoms (and their connections) in a
molecular dynamics simulation dataset.

You can run the script from the command line by typing
python molecules.py

"""

from vtk import *
import molecules_io
import collections
import operator


#needed to determine the path to the source files
from os.path import dirname, realpath, join

# Define a class for the keyboard interface

def MakeLUTFromCTF(tableSize):#taken from http://www.cmake.org/Wiki/VTK/Examples/Python/Visualization/AssignColorsCellFromLUT, python does not seem to support "GetTable" on CTF by default.
    '''
    Use a color transfer Function to generate the colors in the lookup table.
    See: http://www.vtk.org/doc/nightly/html/classvtkColorTransferFunction.html
    :param: tableSize - The table size
    :return: The lookup table.
    '''
    ctf = vtk.vtkColorTransferFunction()
    #ctf.SetColorSpaceToDiverging()

    #taken from http://colorbrewer2.org/, sequential data, colorblind safe.
    ctf.AddRGBPoint(1.0, 255/255.0,255/255.0,217/255.0)
    ctf.AddRGBPoint(0.875, 237/255.0,248/255.0,177/255.0)
    ctf.AddRGBPoint(0.75, 199/255.0,233/255.0,180/255.0)
    ctf.AddRGBPoint(0.625, 127/255.0,205/255.0,187/255.0)
    ctf.AddRGBPoint(0.5, 65/255.0,182/255.0,196/255.0)
    ctf.AddRGBPoint(0.375, 29/255.0,145/255.0,192/255.0)
    ctf.AddRGBPoint(0.25, 34/255.0,94/255.0,168/255.0)
    ctf.AddRGBPoint(0.125, 37/255.0,52/255.0,148/255.0)
    ctf.AddRGBPoint(0.0, 8/255.0,29/255.0,88/255.0)


    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(tableSize)
    lut.Build()

    for i in range(0,tableSize):
        rgb = list(ctf.GetColor(float(i)/tableSize))+[1]
        lut.SetTableValue(i,rgb)

    return lut

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
        # Add your keyboard shortcuts here. If you modify any of the
        # actors or change some other parts or properties of the
        # scene, don't forget to call the render window's Render()
        # function to update the rendering.
        # elif key == ...


# Read the data into a vtkPolyData object using the functions in
# molecules_io.py
basedir = dirname(realpath(__file__)) #Get the directory of the .py file, courtesy of http://stackoverflow.com/a/5137509/4455880

data = vtk.vtkPolyData()
data.SetPoints(molecules_io.read_points(join(basedir, "coordinates.txt")))
data.GetPointData().SetScalars(molecules_io.read_scalars(join(basedir, "radii.txt")))
data.SetLines(molecules_io.read_connections(join(basedir, "connections.txt")))

pd = data.GetPointData()
pd.GetScalars().SetName("radii")
colors = vtkUnsignedCharArray()
colors.SetNumberOfComponents(3)
colors.SetName("Colors")


color_table =[[255,0,0],[128,255,0],[0,255,255],[127,0,255], [255,0,255],[255,127,0],[0,255,0], [0,127,255] ]
color_dictionary = dict()
scalars = data.GetPointData().GetScalars()
current_key = 0;
for i in range(0, scalars.GetNumberOfTuples()):
    scalar = scalars.GetTuple1(i)
    if color_dictionary.has_key(scalar):
        colors.InsertNextTuple(color_dictionary[scalar])
    else:
        color_dictionary[scalar] = color_table[current_key]
        colors.InsertNextTuple(color_table[current_key])
        current_key += 1 #will fail if color_table too small
pd.AddArray(colors)
print(color_dictionary)

sphere_source = vtkSphereSource()

glyph = vtkGlyph3D();
glyph.SetSourceConnection(sphere_source.GetOutputPort());
glyph.SetInput(data)
glyph.SetColorModeToColorByScalar()
glyph.Update()

mapper_molecules = vtkPolyDataMapper()
mapper_connections = vtkPolyDataMapper()
mapper_molecules.SetInputConnection(glyph.GetOutputPort())
mapper_molecules.SetScalarModeToUsePointFieldData()
mapper_molecules.SelectColorArray("Colors")


tube_filter = vtkTubeFilter()
tube_filter.SetInput(data)
tube_filter.SetVaryRadiusToVaryRadiusOff()
tube_filter.SetRadius(0.05)
tube_filter.SetNumberOfSides(15)

mapper_connections.SetInputConnection(tube_filter.GetOutputPort())
#mapper_connections.SetInput(data) #Map with normal lines
#mapper_connections.SetScalarModeToUsePointFieldData()
#mapper_connections.SelectColorArray("Colors")
mapper_connections.ScalarVisibilityOff()

legend = vtkLegendBoxActor()
legend.SetNumberOfEntries(len(color_dictionary)+1)
legend.SetEntryColor(0, 1,1,1)
legend.SetEntryString(0, "RADII:")
sorted_dict = sorted(color_dictionary.items(), key=operator.itemgetter(0))
index = 1
print sorted_dict
for key_color in sorted_dict:
    key = key_color[0]
    color = key_color[1]
    legend.SetEntryColor(index, color[0]/255., color[1]/255., color[2]/255.)
    legend.SetEntryString(index, "%.2f" % key)
    index += 1
legend.SetBackgroundColor(0,0,0)
legend.UseBackgroundOn()
legend.SetPosition(0,0)
#legend.SetBackgroundOpacity(1)

outline = vtkOutlineFilter()
outline.SetInput(data)
mapper_outline = vtkPolyDataMapper()
mapper_outline.SetInputConnection(outline.GetOutputPort())

actor_molecules = vtkActor()
actor_molecules.SetMapper(mapper_molecules)
actor_connections = vtkActor()
actor_connections.SetMapper(mapper_connections)
actor_outline = vtkActor()
actor_outline.SetMapper(mapper_outline)

# Create a renderer and add the actors to it
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.2, 0.2, 0.2)
renderer.AddActor(actor_molecules)
renderer.AddActor(actor_connections)
renderer.AddActor(legend)
renderer.AddActor(actor_outline)

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.SetWindowName("Molecular dynamics")
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
