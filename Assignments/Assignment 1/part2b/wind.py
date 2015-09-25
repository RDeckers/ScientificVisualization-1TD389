"""Air currents.

This script should display a visualization of a vtkStructuredPoints
dataset containing the direction and speed of air currents over North
America.

You can run the script from the command line by typing
python wind.py

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
min_x, max_x, min_y, max_y, min_z, max_z = reader.GetOutput().GetBounds()
center_x, center_y, center_z = reader.GetOutput().GetCenter()

scalar_range = reader.GetOutput().GetPointData().GetScalars().GetRange()
lut = MakeLUTFromCTF(1024)
lut.SetScaleToLog10()
lut.SetTableRange(scalar_range);

scalarBar = vtkScalarBarActor()
scalarBar.SetLookupTable( lut )

bar_coordinates = scalarBar.GetPositionCoordinate()
bar_coordinates.SetCoordinateSystemToNormalizedViewport()
bar_coordinates.SetValue(0.9,0.1)
scalarBar.SetWidth(.1)
scalarBar.SetHeight(.9)
scalarBar.SetTitle( "Wind speed (log)" )

outline = vtkOutlineFilter()
outline.SetInputConnection(reader.GetOutputPort())
mapper_outline = vtkPolyDataMapper()
mapper_outline.SetInputConnection(outline.GetOutputPort())
actor_outline = vtkActor()
actor_outline.SetMapper(mapper_outline)

#sample plane along the bottom, captures vortices
plane_bottom = vtkPlaneSource()
plane_bottom.SetOrigin(min_x,min_y, min_z)
plane_bottom.SetPoint1(min_x, max_y, min_z)
plane_bottom.SetPoint2(max_x, min_y, min_z)
plane_bottom.SetXResolution(10)
plane_bottom.SetYResolution(20)

#sample plane on the main "ingoing" plane, captures general behaviour
plane_source = vtkPlaneSource()
plane_source.SetOrigin(min_x,min_y, min_z)
plane_source.SetPoint1(min_x, min_y, max_z)
plane_source.SetPoint2(max_x, min_y, min_z)
plane_source.SetXResolution(6)
plane_source.SetYResolution(12)

#combine the bottom and source plane
append_filter = vtkAppendPolyData();
append_filter.AddInput(plane_source.GetOutput())
append_filter.AddInput(plane_bottom.GetOutput())
append_filter.Update()


probe_filter = vtkProbeFilter()
probe_filter.SetInput(append_filter.GetOutput())
probe_filter.SetSource(reader.GetOutput())
probe_filter.Update()
probe_mapper = vtkPolyDataMapper()
probe_mapper.SetInputConnection(probe_filter.GetOutputPort())
probe_mapper.SetLookupTable(lut)
probe_mapper.UseLookupTableScalarRangeOn()
probe_actor = vtkActor()
probe_actor.GetProperty().SetOpacity(0.5);
probe_actor.SetMapper(probe_mapper)

integ = vtkRungeKutta4() # integrator for generating the streamlines #
streamer = vtkStreamLine()
streamer.SetInputConnection( reader.GetOutputPort() )
streamer.SetSource( append_filter.GetOutput() )
streamer.SetMaximumPropagationTime(1000)
streamer.SetIntegrationStepLength(.03)
streamer.SetStepLength(.015)
streamer.SetIntegrationDirectionToIntegrateBothDirections()
streamer.SetIntegrator( integ )

streamerMapper = vtk.vtkPolyDataMapper()
streamerMapper.SetInputConnection( streamer.GetOutputPort() )
streamerMapper.SetLookupTable( lut )
streamerMapper.UseLookupTableScalarRangeOn()
streamerActor = vtk.vtkActor()
streamerActor.SetMapper( streamerMapper )
streamerActor.GetProperty().SetOpacity(0.85);

arrow_source = vtkArrowSource()
#arrow_source.SetTipLength(.25)
#arrow_source.SetShaftRadius(0.0)
#
mask = vtkMaskPoints()#speeds things up
mask.SetOnRatio(25)
mask.SetInputConnection(streamer.GetOutputPort())

vertex_filter = vtkVertexGlyphFilter()#needed to work with clean poly
vertex_filter.SetInputConnection(mask.GetOutputPort())

clean = vtkCleanPolyData() #remove any points to close together
clean.SetTolerance(0.01)
#clean.ConvertLinesToPointsOn()
clean.SetInputConnection(vertex_filter.GetOutputPort())

# streamer.Update()
# stream_out = streamer.GetOutput()
# print streamer.GetOutput().GetCell(0).GetPoints()
# stream_output = stream_out.GetPointData().GetVectors()
# stream_lines = stream_out.GetLines()
# stream_scalars = stream_out.GetPointData().GetScalars()
#
# stream_lines.InitTraversal()
# arrow_points = vtkPoints()
# arrow_velocities = vtkFloatArray()
# arrow_vel = vtkFloatArray()
# arrow_vel.SetNumberOfComponents(3)
# arrow_velocities.SetNumberOfComponents(1)
# #arrow_points.SetName("Coords")
#
# radius = 10
# for i in range(0, stream_out.GetNumberOfCells()):
#     points = stream_out.GetCell(i).GetPoints();
#     associated_point_ids = stream_out.GetCell(i).GetPointIds()
#     last_point = points.GetPoint(0)
#     arrow_points.InsertNextPoint(last_point)
#     for j in range(1, points.GetNumberOfPoints()):
#         new_point = points.GetPoint(j)
#         if (new_point[0]-last_point[0])*(new_point[0]-last_point[0])+(new_point[1]-last_point[1])*(new_point[1]-last_point[1])+(new_point[2]-last_point[2])*(new_point[2]-last_point[2]) > radius:
#            arrow_points.InsertNextPoint(new_point)
#            corresponding_vel = stream_output.GetTuple3(associated_point_ids.GetId(j))
#            arrow_vel.InsertNextTuple(corresponding_vel);
#            last_point = new_point
# #print arrow_points.GetNumberOfTuples()
# arrow_point_pd = vtkPolyData()
# arrow_point_pd.SetPoints(arrow_points)
# arrow_point_pd.GetPointData().SetVectors(arrow_vel)
# #arrow_point_pd.GetPointData().SetScalars(stream_scalars)
# print arrow_point_pd.GetNumberOfPoints()
# print arrow_point_pd
# #arrow_point_pd.GetSetNumberOfPoints(arrow_points.GetNumberOfTuples())
# arrow_point_pd.ComputeBounds()
glyph = vtkGlyph3D();
glyph.SetScaleModeToDataScalingOff()
# mask.Update()
# print mask.GetOutput()
glyph.SetSourceConnection(arrow_source.GetOutputPort());
#glyph.SetInput(arrow_point_pd)
glyph.SetInputConnection(clean.GetOutputPort())
glyph.Update()

mapper_arrow = vtkPolyDataMapper()
mapper_arrow.SetInputConnection(glyph.GetOutputPort())
mapper_arrow.SetLookupTable(lut)
mapper_arrow.UseLookupTableScalarRangeOn()
#mapper_arrow.SetScalarModeToUsePointFieldData()
#mapper_arrow.SelectColorArray("Colors")
actor_arrow = vtkActor()
actor_arrow.SetMapper(mapper_arrow)

geom_filter = vtkGeometryFilter()
geom_filter.SetInputConnection(streamer.GetOutputPort())
#glyph.SetColorModeToColorByScalar()

# Create a renderer and add the actors to it
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.2, 0.2, 0.2)
renderer.AddActor(actor_outline)
renderer.AddActor(scalarBar)
renderer.AddActor(streamerActor)
renderer.AddActor(probe_actor)
renderer.AddActor(actor_arrow)

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.SetWindowName("Air currents")
render_window.SetSize(1024, 800)
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
