Flow simulation
===============

``viscosity``
-------------

**Type:** positive number. **Units:** m²/s. Kinematic viscosity, equal to dynamic
viscosity divided by fluid density.

.. _inlet-location:

``inletLocation``
-----------------

**Type:** string. **Accepted values:** ``left``, ``top``, ``right``, or
``bottom``. Selects the injection side. In device mode, ``top`` corresponds to
the top-left entry and ``right`` to the top-right entry, with analogous mapping
for the other sides.

``inletValue``
--------------

**Type:** nonnegative number. **Units:** Pa/(kg/m³). Pressure divided by fluid
density at the inlet.

``pressureConv`` and ``velocityConv``
-------------------------------------

**Type:** positive number. Convergence criteria for pressure and velocity in the
steady flow simulation.

``iterationsMax``
-----------------

**Type:** positive integer. Maximum steady-flow iterations if convergence has
not been reached.

The OpenFOAM case templates remain editable after generation. Refer to the
OpenFOAM documentation for the solver configuration and numerical schemes.
