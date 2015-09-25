# File:        ctscan.py
# Description: MPR rendering

from vtk import *
#needed to determine the path to the source files
from os.path import dirname, realpath, join

def get_binary_relative_file(filepath):
    basedir = dirname(realpath(__file__)) #Get the directory of the .py file, courtesy of http://stackoverflow.com/a/5137509/4455880
    return join(basedir, filepath)

# Python function for the keyboard interface
# count is a screenshot counter
count = 0
def Keypress(obj, event):
    global count, iv
    key = obj.GetKeySym()
    if key == "s":
        render_window.Render()
        w2if.Modified() # tell the w2if that it should update
        fnm = "screenshot%02d.png" %(count)
        wr.SetFileName(fnm)
        wr.Write()
        print "Saved '%s'" %(fnm)
        count = count+1
    elif key == "n": #rotate between raw marching_cubes, sinc_smoothed, and sinc_smoothed with recomputed normals.
        global current_output_filter
        global filter_outputs
        current_output_filter = (current_output_filter + 1) % 3
        cubes_mapper.SetInputConnection(filter_outputs[current_output_filter])
        render_window.Render()
    elif key == "h":
        cubes_actor.SetVisibility(not cubes_actor.GetVisibility())
        render_window.Render()


    # add your keyboard interface here
    # elif key == ...

# image reader
reader_ct = vtk.vtkStructuredPointsReader()
reader_ct.SetFileName( get_binary_relative_file("data/ctscan.vtk") )
reader_ct.Update()

W,H,D = reader_ct.GetOutput().GetDimensions()
a1,b1 = reader_ct.GetOutput().GetScalarRange()
print "Range of image: [%d, %d]" %(a1,b1)

reader_liver = vtk.vtkStructuredPointsReader()
reader_liver.SetFileName( get_binary_relative_file("data/liver_bin.vtk") )
reader_liver.Update()

a2,b2 = reader_liver.GetOutput().GetScalarRange()
print "Range of segmented image: [%d, %d]" %(a2,b2)

# renderer and render window
renderer = vtk.vtkRenderer()
renderer.SetBackground(.2, .2, .2)
render_window = vtk.vtkRenderWindow()
render_window.SetSize( 512, 512 )
render_window.AddRenderer( renderer )

# render window interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow( render_window )

# liver_smart_mapper = vtkSmartVolumeMapper();
marching_cubes = vtkMarchingCubes()#TODO: buffering, tweak isovalue
marching_cubes.SetInputConnection(reader_liver.GetOutputPort())
marching_cubes.SetNumberOfContours(1)
marching_cubes.SetValue(0, 255)
marching_cubes.ComputeNormalsOff()
marching_cubes.ComputeScalarsOff()
#marching_cubes.GenerateValues(5, 50, 3000)

sinc_filter = vtkWindowedSincPolyDataFilter()
sinc_filter.SetInputConnection(marching_cubes.GetOutputPort())

normal_generator = vtkPolyDataNormals()
normal_generator.SetInputConnection(sinc_filter.GetOutputPort());
normal_generator.ComputePointNormalsOn();
normal_generator.ComputeCellNormalsOn();

filter_outputs = [marching_cubes.GetOutputPort(), sinc_filter.GetOutputPort(), normal_generator.GetOutputPort()]
current_output_filter = 0;

cubes_mapper = vtkPolyDataMapper()
cubes_mapper.SetInputConnection(filter_outputs[current_output_filter])

cubes_actor = vtkActor()
cubes_actor.SetMapper(cubes_mapper)
cubes_actor.GetProperty().SetColor(108.0/255, 46.0/255, 31.0/255) #liver color

renderer.AddActor(cubes_actor)

picker = vtkCellPicker() # use same picker for all
picker.SetTolerance(0.005)

plane_x = vtkImagePlaneWidget()
plane_x.SetPicker(picker)
plane_x.SetInput(reader_ct.GetOutput())
plane_x.SetCurrentRenderer(renderer)
plane_x.SetInteractor(interactor)
plane_x.SetSliceIndex(W/2)
plane_x.DisplayTextOn()
plane_x.EnabledOn()
plane_x.PlaceWidget()
plane_x.SetPlaneOrientationToXAxes()

plane_y = vtkImagePlaneWidget()
plane_y.SetPicker(picker)
plane_y.SetInput(reader_ct.GetOutput())
plane_y.SetCurrentRenderer(renderer)
plane_y.SetInteractor(interactor)
plane_y.SetSliceIndex(W/2)
plane_y.DisplayTextOn()
plane_y.EnabledOn()
plane_y.PlaceWidget()
plane_y.SetPlaneOrientationToYAxes()

plane_z = vtkImagePlaneWidget()
plane_z.SetPicker(picker)
plane_z.SetInput(reader_ct.GetOutput())
plane_z.SetCurrentRenderer(renderer)
plane_z.SetInteractor(interactor)
plane_z.SetSliceIndex(W/2)
plane_z.DisplayTextOn()
plane_z.EnabledOn()
plane_z.PlaceWidget()
plane_z.SetPlaneOrientationToZAxes()

# create an outline of the dataset
outline = vtk.vtkOutlineFilter()
outline.SetInput( reader_ct.GetOutput() )
outline_mapper = vtk.vtkPolyDataMapper()
outline_mapper.SetInput( outline.GetOutput() )
outline_actor = vtk.vtkActor()
outline_actor.SetMapper( outline_mapper )

# the actors property defines color, shading, line width,...
outline_actor.GetProperty().SetColor(0.8,0.8,0.8)
outline_actor.GetProperty().SetLineWidth(2.0)

# add the actors
renderer.AddActor( outline_actor )
render_window.Render()

# create window to image filter to get the window to an image
w2if = vtk.vtkWindowToImageFilter()
w2if.SetInput(render_window)

# create png writer
wr = vtk.vtkPNGWriter()
wr.SetInput(w2if.GetOutput())

# add keyboard interface, initialize, and start the interactor
interactor.AddObserver("KeyPressEvent", Keypress)
interactor.Initialize()
interactor.Start()
