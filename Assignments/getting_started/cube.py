"""Simple VTK scene.

This script displays a simple 3D scene containing a single actor (a
cube) that the user can interact with via the mouse and keyboard. The
purpose of the script is to illustrate the VTK visualization pipeline
and how to use VTK in Python.

You can run the script from the command line by typing
python isosurface.py

"""

import vtk

# Generate polygon data for a cube
cube = vtk.vtkCubeSource()

# Create a mapper and an actor for the cube data
cube_mapper = vtk.vtkPolyDataMapper()
cube_mapper.SetInput(cube.GetOutput())
cube_actor = vtk.vtkActor()
cube_actor.SetMapper(cube_mapper)
cube_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # make the cube red

# Create a renderer and add the cube actor to it
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.0, 0.0, 0.0)  # make the background black
renderer.AddActor(cube_actor)

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.SetWindowName("Simple VTK scene")
render_window.SetSize(400, 400)
render_window.AddRenderer(renderer)

# Create an interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Initialize the interactor and start the rendering loop
interactor.Initialize()
render_window.Render()
interactor.Start()
