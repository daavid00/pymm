6. Run the complete workflow
============================

Goal
----
Generate the mesh and both simulations with one command.

Command
-------

.. code-block:: console

   pymm -i microsystem.png -p parameters.toml -t all

How it works
------------
The ``all`` workflow executes image processing, mesh generation, steady flow,
and tracer transport in dependency order.

Result
------
The output contains diagnostic PNGs, Gmsh input and mesh files, editable
OpenFOAM cases, and VTK exports.

.. code-block:: text

   output/
   ├── binary_image.png
   └── extracted_border.png
   └── interior_grains_border.png
   └── interior_grains.png
   └── mesh.geo
   └── mesh.msh
   └── VTK_flowStokes/
   └── VTK_tracerTransport/
   └── OpenFOAM/
       ├──flowStokes/
       └──tracerTransport/
