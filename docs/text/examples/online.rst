Online micromodel
=================

Overview
--------

This case uses the micromodel shown in Fig. 2a of `Joekar-Niasar et al. (2009)
<https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2007WR006641>`_. The
image was captured as ``online.png`` with 1068 × 1068 pixels.

Configuration
-------------

.. code-block:: toml
   :linenos:

   length = 600e-6       # Image-related, length of the microsystem [m]
   width = 600e-6        # Image-related, height of the microsystem [m]
   thickness = 1.8e-6    # Image-related, depth of the microsystem [m]
   grainMeaning = 1      # Image-related, 0 for light grains or 1 for dark grains
   threshold = 0.5       # Image-related, threshold for converting the image to binary
   rescale = 1           # Image-related, rescaling factor for the input image
   grainsSize = 50       # Image-related, minimum size of the grain clusters
   borderTol = 1         # Image-related, tolerance for approximating the border as a polygon
   grainsTol = 1         # Image-related, tolerance for approximating the grains as polygons
   lineWidth = 1         # Figure-related, line width for contours in the generated figures
   channelWidth = 6e-6   # Device-related, width of the top and bottom channels [m]
   meshSize = 1e-6       # Mesh-related, mesh size [m]
   viscosity = 1e-6      # Fluid-related, kinematic viscosity [m2/s]
   diffusion = 1e-12     # Fluid-related, tracer diffusion coefficient [m2/s]
   inletLocation = "top" # Simulation-related, inlet location: left, top, right, or bottom
   inletValue = 2.0e-3   # Simulation-related, inlet pressure divided by fluid density [Pa/(kg/m3)]
   tracerTime = 120      # Simulation-related, end time for the tracer simulation [s]
   tracerWrite = 1       # Simulation-related, interval for writing tracer results [s]
   pressureConv = 1e-7   # Solver-related, pressure convergence criterion
   velocityConv = 1e-8   # Solver-related, velocity convergence criterion
   iterationsMax = 10000 # Solver-related, maximum number of Stokes iterations
   tracerStep = 1        # Solver-related, tracer simulation time step [s]

Command
-------

A source-built Gmsh executable was supplied with the canonical ``--gmsh`` flag:

.. code-block:: console

   pymm -i online.png -p configuration.toml -m device -t all --gmsh /home/AD.NORCERESEARCH.NO/dmar/Github/gmsh/build/gmsh

The reported execution time was approximately 15 minutes.

Results
-------

.. figure:: ../figs/online_pressure.png
   :alt: Pressure field for the online micromodel

.. figure:: ../figs/online_velocity.png
   :alt: Velocity field for the online micromodel

.. figure:: ../figs/online_tracer.png
   :alt: Tracer concentration for the online micromodel

   Pressure, velocity, and tracer concentration.

.. button-ref:: ../examples
   :color: primary

   Back to examples gallery
