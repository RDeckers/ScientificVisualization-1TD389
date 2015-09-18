"""Isosurface extraction.

This script should extract and display isosurfaces of the probability
density of a hydrogen atom in a volume dataset.

You can run the script from the command line by typing
python isosurface.py

"""

from vtk import *

#needed to determine the path to the source files
from os.path import dirname, realpath, join

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

# Define a class for the keyboard interface
class KeyboardInterface(object):
    """Keyboard interface.

    Provides a simple keyboard interface for interaction. You should
    extend this interface with keyboard shortcuts for changing the
    isovalue interactively.

    """

    def __init__(self): #TODO: Read up op Python classes, move initialization into here, absorb an relevant variables.
        self.screenshot_counter = 0
        self.contour_value = 0.5
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
        elif key == "Up":
            self.contour_value += 0.005
            contour_filter.SetValue(0, self.contour_value)
            text_actor.SetInput("Iso = %.3f" % self.contour_value)
            render_window.Render()
        elif key == "Down":
            self.contour_value -= 0.005
            contour_filter.SetValue(0, self.contour_value)
            text_actor.SetInput("Iso = %.3f" % self.contour_value)
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
contour_filter.ComputeGradientsOn()#we want the gradients for colouring
#contour_filter.ComputeScalarsOff()#these will be constant over an isosurface....
contour_filter.Update();
surface_mapper = vtkPolyDataMapper()
surface_mapper.SetInputConnection(contour_filter.GetOutputPort())
#print(contour_filter.GetOutput())
surface_mapper.SetScalarModeToUsePointFieldData()
surface_mapper.SelectColorArray("Gradients")
surface_mapper.UseLookupTableScalarRangeOn()
#help(color_transfer.__class__)
lut = MakeLUTFromCTF(1024)
#table = color_transfer.GetTable(0, 1, 4096)
lut.SetVectorModeToMagnitude()
#TODO: controls for table-range, scaling, automatic adjustment based on range at given contour.
lut.SetTableRange(0,0.3)

surface_mapper.SetLookupTable(lut)
#print(lut.GetValueRange())
#print(surface_mapper)

surface_actor = vtkActor()
surface_actor.SetMapper(surface_mapper)

bar_actor = vtkScalarBarActor()
bar_actor.SetLookupTable(lut)
bar_coordinates = bar_actor.GetPositionCoordinate()
bar_coordinates.SetCoordinateSystemToNormalizedViewport()
bar_coordinates.SetValue(0.9,0.1)
bar_actor.SetWidth(.1)
bar_actor.SetHeight(.9)
bar_actor.SetTitle( "Divergence" )

text_actor = vtkTextActor()
text_actor.SetInput("Iso = 0.500")
text_actor.SetTextScaleModeToViewport()

# Create a renderer and add the actors to it
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.2, 0.2, 0.2)
renderer.AddActor(outline_actor)
renderer.AddActor(surface_actor)
renderer.AddActor(bar_actor)
renderer.AddActor(text_actor)

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
