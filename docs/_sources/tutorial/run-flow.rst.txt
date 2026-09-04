2. Run the flow simulation
==========================

Goal
----
Reuse the generated mesh and compute the steady velocity and pressure fields.

Configuration
-------------
The flow stage uses ``viscosity``, ``inletLocation``, ``inletValue``,
``pressureConv``, ``velocityConv``, and ``iterationsMax``.

Command
-------

.. code-block:: console

   pymm -p parameters.toml -t flow

How it works
------------
pymm creates the OpenFOAM flow case, runs ``gmshToFoam``, executes ``foamRun``
with the incompressible-fluid solver, and converts the result using
``foamToVTK``.

Result
------
Results are written below ``OpenFOAM/flowStokes`` and ``VTK_flowStokes``.

Next
----
Continue with :doc:`run-tracer`.
