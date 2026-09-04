Complete TOML example
=====================

.. code-block:: toml
   :linenos:

   # Physical microsystem dimensions [m]
   length = 6.74e-3
   width = 2.5e-3
   thickness = 0.03e-3

   # Image segmentation and contour extraction
   grainMeaning = 1      # 0: light grains; 1: dark grains
   threshold = 0.5       # Grayscale threshold in [0, 1]
   rescale = 1           # Positive image rescaling factor
   grainsSize = 0        # Small-object size threshold [pixels]
   borderTol = 0         # External-border polygon tolerance
   grainsTol = 0         # Interior-grain polygon tolerance

   # Figures, device geometry, and mesh
   lineWidth = 1
   channelWidth = 0.2e-3 # Device-channel width [m]
   meshSize = 8e-6       # Target mesh size [m]

   # Fluid and tracer properties
   viscosity = 1e-6      # Kinematic viscosity [m2/s]
   diffusion = 1e-12     # Tracer diffusion coefficient [m2/s]

   # Boundary conditions and simulation controls
   inletLocation = "top" # left, top, right, or bottom
   inletValue = 5.0e-4   # Pressure divided by density [Pa/(kg/m3)]
   tracerTime = 120      # Tracer end time [s]
   tracerWrite = 1       # Tracer write interval [s]
   pressureConv = 1e-7   # Pressure convergence criterion
   velocityConv = 1e-8   # Velocity convergence criterion
   iterationsMax = 10000 # Maximum steady-flow iterations
   tracerStep = 1        # Tracer time step [s]
