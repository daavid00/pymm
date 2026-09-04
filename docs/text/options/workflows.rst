Workflow behavior
=================

``pngs``
--------
Process the image and write segmentation and contour figures.

``mesh``
--------
Process the image and create ``mesh.geo`` and ``mesh.msh``. Requires Gmsh.

``flow``
--------
Keep the existing mesh and run steady flow. Requires ``mesh.msh`` and
``gmshToFoam``.

``mesh_flow``
-------------
Generate the mesh and then run steady flow.

``flow_tracer``
---------------
Run steady flow and then tracer transport. Requires an existing mesh.

``tracer``
----------
Run only tracer transport. Requires an existing ``OpenFOAM/flowStokes`` case
and the ``topoSet`` utility.

``all``
-------
Run image processing, meshing, flow, and tracer transport.

Invalid prerequisites are fatal command-line errors. External solver failures
are reported by their subprocess exit status.
