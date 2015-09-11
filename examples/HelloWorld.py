# This program demonstrates how VTK can be used to render a text
# The user can also interact with the text by using the mouse

# load VTK
import vtk

# Create a Text source and set the text
text = vtk.vtkTextSource()
text.SetText("UPPMAX")
text.SetForegroundColor(0.6,0.2,0.2)

# Create a mapper and set the Text source as input
textMapper = vtk.vtkPolyDataMapper()
textMapper.SetInputConnection(text.GetOutputPort())

# Create an actor and set the mapper as input
textActor = vtk.vtkActor()
textActor.SetMapper(textMapper)

# Create a renderer
ren = vtk.vtkRenderer()

# Assign the actor to the renderer
ren.AddActor(textActor)

# Create a rendering window
renWin = vtk.vtkRenderWindow()

# Add the renderer to the window
renWin.AddRenderer(ren)

# Set the name of the window (this is optional)
renWin.SetWindowName("Hello World!")

# Make sure that we can interact with the application
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Initialze and start the application
iren.Initialize()
iren.Start()
