"""

This example shows how to create a vtkPolyData object with multiple
scalar attributes (strength and time), and how to efficiently extract
quakes within a specified time interval.

Author: Johan Nysjo

"""

import ReadPointsCSV
import vtk

# Load the earthquake data
points, strength, time_, = ReadPointsCSV.readPoints("events3.csv")
min_strength, max_strength = strength.GetRange()
min_time, max_time = time_.GetRange()  # in seconds

# Assign unique names to the scalar arrays
strength.SetName("strength")
time_.SetName("time")

# Create a vtkPolyData object from the earthquake data and specify
# that "strength" should be the active scalar array
points_polydata = vtk.vtkPolyData()
points_polydata.SetPoints(points)
points_polydata.GetPointData().AddArray(strength)
points_polydata.GetPointData().AddArray(time_)
points_polydata.GetPointData().SetActiveScalars("strength")

# Threshold the earthquake points to extract all points within a
# specified time interval.
#
# If you do not specify which input array to process, i.e., if you
# comment out the SetInputArrayToProcess() call, the thresholding will
# be performed on the active scalar array ("strength", in this case).
threshold_filter = vtk.vtkThresholdPoints()
threshold_filter.SetInput(points_polydata)
threshold_filter.ThresholdBetween(min_time, max_time)
threshold_filter.SetInputArrayToProcess(0, 0, 0, 0, "time")
threshold_filter.Update()

# Connect the output of the threshold filter to a vtkGlyph3D filter
# and proceed with the visualization!
