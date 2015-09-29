# File:        ctscan.py
# Description: MPR rendering

from vtk import *
#needed to determine the path to the source files
from os.path import dirname, realpath, join

def get_binary_relative_file(filepath):
    basedir = dirname(realpath(__file__)) #Get the directory of the .py file, courtesy of http://stackoverflow.com/a/5137509/4455880
    return join(basedir, filepath)

class TransferMethod:
    color_transfer = vtkColorTransferFunction()
    opacity_transfer = vtkPiecewiseFunction()
    global_opacity = 0.5
    lower_bound = 0
    upper_bound = 100
    bound_width = 0.01
    low_oob = [0,0,0,0]
    low_colour = [0,0,0]
    mid_colour = [0.5,0.5,0.5]
    high_colour = [1,1,1]
    high_oob = [1,0,0,1]
    def __init__(self):
        self.update()
    def get_color(self):
        return self.color_transfer
    def get_opacity(self):
        return self.opacity_transfer
    def set_colors(self, low_color, mid_color, high_color):
        self.low_colour = low_color
        self.high_colour = high_color
        self.mid_colour = mid_color
    def update(self):
        self.color_transfer.RemoveAllPoints()
        self.color_transfer.AddRGBPoint(self.lower_bound-self.bound_width,self.low_oob[0], self.low_oob[1],self.low_oob[2])
        self.color_transfer.AddRGBPoint(self.lower_bound, self.low_colour[0], self.low_colour[1],self.low_colour[2])
        self.color_transfer.AddRGBPoint(self.lower_bound+(self.upper_bound-self.lower_bound)/2, self.mid_colour[0], self.mid_colour[1],self.mid_colour[2])
        self.color_transfer.AddRGBPoint(self.upper_bound, self.high_colour[0], self.high_colour[1],self.high_colour[2])
        self.color_transfer.AddRGBPoint(self.upper_bound+self.bound_width, self.high_oob[0], self.high_oob[1],self.high_oob[2])

        self.opacity_transfer.RemoveAllPoints()
        self.opacity_transfer.AddPoint(self.lower_bound-self.bound_width,self.low_oob[3])
        self.opacity_transfer.AddPoint(self.lower_bound, self.global_opacity)
        self.opacity_transfer.AddPoint(self.lower_bound+(self.upper_bound-self.lower_bound)/2, self.global_opacity)
        self.opacity_transfer.AddPoint(self.upper_bound, self.global_opacity)
        self.opacity_transfer.AddPoint(self.upper_bound+self.bound_width, self.high_oob[3])
    def set_range(self, low, high):
        self.upper_bound = high
        self.lower_bound = low
    def get_lower_bound(self):
        return self.lower_bound
    def get_upper_bound(self):
        return self.upper_bound
    def set_lower_bound(self, bound):
        self.lower_bound = bound
    def set_colors(self, low, mid, high):
        self.low_colour = low
        self.mid_colour = mid
        self.high_colour = high
    def get_global_opacity(self):
        return self.global_opacity
    def set_global_opacity(self, opacity):
        self.global_opacity = opacity
    # def set_lower_bound(self, bound, oob_colour):
    #     self.lower_bound = bound
    #     self.low_oob = oob_colour
    def set_upper_bound(self, bound):
        self.upper_bound = bound
    def set_oob_colours(self, low, high):
        self.low_oob = low
        self.high_oob = high
    # def set_upper_bound(self, bound, oob_colour):
    #     self.upper_bound = bound
    #     self.high_oob = oob_colour

# Python function for the keyboard interface
# count is a screenshot counter
count = 0
def Keypress(obj, event):
    global count, iv, transfer_function,volumeProperty, volume
    key = obj.GetKeySym()
    if key == "9":
        render_window.Render()
        w2if.Modified() # tell the w2if that it should update
        fnm = "screenshot%02d.png" %(count)
        wr.SetFileName(fnm)
        wr.Write()
        print "Saved '%s'" %(fnm)
        count = count+1
    elif key == "h":
        cubes_actor.SetVisibility(not cubes_actor.GetVisibility())
        render_window.Render()
    elif key == "a":
        upper_bound = transfer_function.get_upper_bound()+1
        transfer_function.set_upper_bound(upper_bound)
        transfer_function.update()
        volumeProperty.SetColor(transfer_function.get_color())
        volumeProperty.SetScalarOpacity(transfer_function.get_opacity())
        render_window.Render()
    elif key == "z":
        lower_bound = transfer_function.get_lower_bound()
        upper_bound = transfer_function.get_upper_bound()-1
        upper_bound = max(upper_bound, lower_bound)
        transfer_function.set_upper_bound(upper_bound)
        transfer_function.update()
        volumeProperty.SetColor(transfer_function.get_color())
        volumeProperty.SetScalarOpacity(transfer_function.get_opacity())
        render_window.Render()
    elif key == "s":
        upper_bound = transfer_function.get_upper_bound()
        lower_bound = transfer_function.get_lower_bound()+1
        lower_bound = min(lower_bound, upper_bound)
        transfer_function.set_lower_bound(lower_bound)
        transfer_function.update()
        volumeProperty.SetColor(transfer_function.get_color())
        volumeProperty.SetScalarOpacity(transfer_function.get_opacity())
        render_window.Render()
    elif key == "x":
        lower_bound = transfer_function.get_lower_bound()-1
        transfer_function.set_lower_bound(lower_bound)
        transfer_function.update()
        volumeProperty.SetColor(transfer_function.get_color())
        volumeProperty.SetScalarOpacity(transfer_function.get_opacity())
        render_window.Render()
    elif key == "c":
        opacity = transfer_function.get_global_opacity()-0.01
        opacity = max(0, opacity)
        transfer_function.set_global_opacity(opacity)
        transfer_function.update()
        volumeProperty.SetScalarOpacity(transfer_function.get_opacity())
        render_window.Render()
    elif key == "d":
        opacity = transfer_function.get_global_opacity()+0.01
        opacity = min(1, opacity)
        transfer_function.set_global_opacity(opacity)
        transfer_function.update()
        volumeProperty.SetScalarOpacity(transfer_function.get_opacity())
        render_window.Render()
    # elif key == ...

# image reader
reader = vtk.vtkStructuredPointsReader()
reader.SetFileName( get_binary_relative_file("../data/foot.vtk") )
reader.Update()

W,H,D = reader.GetOutput().GetDimensions()
a1,b1 = reader.GetOutput().GetScalarRange()
print "Range of image: [%d, %d]" %(a1,b1)

# renderer and render window
renderer = vtk.vtkRenderer()
renderer.SetBackground(.2, .2, .2)
render_window = vtk.vtkRenderWindow()
render_window.SetSize( 512, 512 )
render_window.AddRenderer( renderer )

# render window interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow( render_window )



transfer_function = TransferMethod()
#transfer_function.add_point(0,0,0,0,0)
bone_bound = 90
flesh_bound = 30
opacity = 0.15
transfer_function.set_range(flesh_bound, bone_bound)
low_color = [253/255.0,187/255.0,132/255.0, opacity]
mid_color = [227/255.0,74/255.0,51/255.0, opacity]
high_color = [0.4,0.1,0.25, opacity]
transfer_function.set_colors(low_color, mid_color, high_color)
transfer_function.set_oob_colours([253/255.0,224/255.0,221/255.0,0], [227/255.0, 218/255.0, 201/255.0,1])
transfer_function.update()


scalar_bar = vtkScalarBarActor()
scalar_bar.SetLookupTable(transfer_function.get_color())

# The property describes how the data will look
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(transfer_function.get_color())
volumeProperty.SetScalarOpacity(transfer_function.get_opacity())
volumeProperty.ShadeOn()
volumeProperty.SetInterpolationTypeToLinear()

# The mapper, uses the volumeProperty for rendering, but always picks the best method in terms of speed.
volumeMapper = vtkSmartVolumeMapper()
volumeMapper.SetInputConnection(reader.GetOutputPort())

acumulator = vtkImageAccumulate()
acumulator.SetInputConnection(reader.GetOutputPort())
acumulator.Update()

histogram_actor = vtkXYPlotActor()
histogram_actor.AddInput(acumulator.GetOutput())
histogram_actor.SetXRange(0, 170)
histogram_actor.SetYRange(0, 200000)
coordinates = histogram_actor.GetPositionCoordinate()
coordinates.SetCoordinateSystemToNormalizedViewport()
coordinates.SetValue(0.0,0.0)
histogram_actor.SetWidth(0.6)
histogram_actor.SetHeight(0.4)
histogram_actor.SetYLabelFormat("")
histogram_actor.SetYTitle ("")
histogram_actor.SetXTitle ("value")
# scalarBar.SetWidth(.1)
# scalarBar.SetHeight(.9)

# The volume holds the mapper and the property and
# can be used to position/orient the volume
volume = vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)

renderer.AddActor(scalar_bar)
renderer.AddVolume(volume)
renderer.AddActor(histogram_actor)


# create an outline of the dataset
outline = vtk.vtkOutlineFilter()
outline.SetInput( reader.GetOutput() )
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
