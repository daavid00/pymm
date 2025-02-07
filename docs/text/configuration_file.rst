==================
Configuration file
==================
Let us consider the image below (this image and the real dimensions can be 
extracted from Fig. 52 in `Benali2019 <https://hdl.handle.net/1956/21300>`_ and Fig. 1c 
in `Liu2022 <https://doi.org/10.1016/j.ijggc.2023.103885>`_). 

.. figure:: figs/microsystem.png

    Grains and pore space configuration.

This image (2D) consists of 805x252 pixels, and the real dimensions (3D) are 6.74e-3 x 2.5e-3 x 0.03e-3 [m]. 
We remark that the image of the pattern used in the numerical simulations in `Liu2022 <https://doi.org/10.1016/j.ijggc.2023.103885>`_
has a much higher resolution.

The current implementation allows for the following input parameters:

.. code-block:: python
    :linenos:

    #Set the pymm parameters
    lenght = 6.74e-3      #Image-related, length of the microsystem [m]
    width = 2.5e-3        #Image-related, height of the microsystem [m]
    tickness = 0.03e-3    #Image-related, depth of the microsystem [m]
    grainMeaning = 1      #Image-related, 0 if the grains in the image are light colors (e.g., white) or 1 for dark colors (e.g., black)
    threshold = 0.5       #Image-related, threshold for converting the image to binary
    rescale = 1           #Image-related, rescaled factor for the input image
    grainsSize = 0        #Image-related, minimum size of the grain clusters
    borderTol = 0         #Image-related, tolerance to approximate the border as polygon
    grainsTol = 0         #Image-related, tolerance to approximate the grains as polygon
    lineWidth = 1         #Figure-related, line width to show the contours in the produced figures
    channelWidth = 0.2e-3 #Device-related, width of the top and bottom channels in the micromodel device [m]
    meshSize = 8e-6       #Mesh-related, mesh size [m]
    viscocity = 1e-6      #Fluid-related, kinematic viscosity [dynamic viscosity/fluid_density, m2/s]
    diffusion = 1e-12     #Fluid-related, diffusion coefficient for the tracer [m2/s]
    inletLocation = "top" #Simulation-related, inlet bc location (left, top, right, or bottom)
    inletValue = 5.0e-4   #Simulation-related, inlet bc value (pressure/fluid_density, [Pa/(kg/m3)])
    tracerTime = 120      #Simulation-related, end time for the tracer simulation [s]
    tracerWrite = 1       #Simulation-related, time interval to write the tracer results [s]
    pressureConv = 1e-7   #Solver-related, convergence criterium for the pressure solution in the numerical scheme for the Stokes simulation
    velocityConv = 1e-8   #Solver-related, convergence criterium for the velocity solution in the numerical scheme for the Stokes simulation
    iterationsMax = 10000 #Solver-related, maximum number of iterations for the Stokes simulation in case the convergence criteria have not been reached
    tracerStep = 1        #Solver-related, time step in the numerical scheme for the tracer simulation [s]

************************
Image-related parameters
************************

The three first parameters set the real dimensions of the microsystem. The next parameter sets the meaning of the grains in the image, i.e., 
0 if the grains in the image are light colors (e.g., white) or 1 for dark colors (e.g., black) The following parameter sets the threshold 
value to convert the image to binary, which is internally converted to gray scale (valid values from 0 to 1). The rescaled factor parameter reduces the number
of pixels of the image (valid values between 0 and 1, see 
`skimage.transform.rescale <https://scikit-image.org/docs/stable/api/skimage.transform.html#skimage.transform.rescale>`_). 
The minimum size of the grain clusters controls the number of pixels to consider for the internal grains (valid values are
greater than 0, see `porespy.filters.trim\_small\_clusters <https://porespy.org/modules/generated/porespy.filters.trim\_small\_clusters.html>`_ ). 
The two following parameters, for setting the tolerance to approximate the contours of polygons, reduce the number of points in the extracted border 
and internal grains respectively (valid values are 0 or greater than 0, see `skimage.measure.approximate\_polygon <https://scikit-image.org/docs/stable/auto\_examples/edges/plot\_polygon.html>`_ ). 
The following figure shows the internal grains and border for three decreasing values of the minimum size cluster and tolerances.

.. figure:: figs/size_500_5_5.png
.. figure:: figs/size_100_1_1.png
.. figure:: figs/size_0_0_0.png

    Extracted contours for minimum size of the cluster grains and tolerances for the polygon approximation of (top) 500, 5, 5, (middle) 100, 1, 1, and (bottom) 0, 0, 0, respectively.

.. tip::
    The smaller are these numbers, the more detail is included in the mesh; however, this increases the execution
    time to create the mesh and to run the simulations. 

*************************************
Figure- and device-related parameters
*************************************

The figure parameter controls the line width of the contours on the output images, while the device parameter controls the
width of the channels in the device microsystem (see the following subsection for details about the implemented device).

***********************
Mesh-related parameters
***********************

Currently the only input parameter (via de configuration file, one can always modify the template files) for the mesh is 
the mesh size. The following figure shows the generated mesh for two different mesh sizes.

.. figure:: figs/mesh_1e4.png
.. figure:: figs/mesh_1e5.png

    Two different generated meshes of sizes (top) 1e-4 and (bottom) 1e-5.

There are currently two template files that define the configuration of the microsystem: image.mako and device.mako.
The template image.mako set the computational grid to the extend of the image, while device.mako creates the micromodel geometry as in 
`Benali2019 <https://hdl.handle.net/1956/21300>`_ and `Liu2022 <https://doi.org/10.1016/j.ijggc.2023.103885>`_. On the grains and device walls we consider no-slip conditions. Then one could look at those files to modify the values 
(e.g., to create quad elements for the mesh) or to define new micromodel geometries (e.g., a micromodel with a vertical cross-type shape).
The following figure shows the geometry of the device micromodel.

.. figure:: figs/device.png

    Geometry of the device mode.

********************
Remaining parameters
********************

The remaining parameters are OpenFOAM related. For example, **inletLocation** sets the side where the fluid is injected, and for the device,  
'top' corresponds to the left top entry, 'right' to the top right entry, etc. Refer to the online OpenFOAM resources for details about
the simulator and `this nice presentation <https://www.slideshare.net/ElwardiFadli/permeability-of-soils>`_ 
using the OpenFOAM solver simpleFoam in another micromodel application. Details about the solver simpleFoam 
and mathematical model can be found `in this link <https://openfoamwiki.net/index.php/OpenFOAM_guide/The_SIMPLE_algorithm_in_OpenFOAM>`_.
Details about the solver scalarTransportFoam and mathematical model can be found `here <https://openfoamwiki.net/index.php/ScalarTransportFoam>`_.
