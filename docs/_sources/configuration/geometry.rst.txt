Grid and geometry
=================

``length``, ``width``, and ``thickness``
----------------------------------------

**Type:** positive number. **Units:** metres. **Required:** yes. These values set
the physical length, height, and extrusion depth of the microsystem.

.. code-block:: toml

   length = 6.74e-3
   width = 2.5e-3
   thickness = 0.03e-3

``lineWidth``
-------------

**Type:** positive number. Controls contour line width in generated diagnostic
figures. It does not affect the mesh.

``channelWidth``
----------------

**Type:** positive number. **Units:** metres. Controls the top and bottom channel
width in ``device`` mode.

.. _mesh-size:

``meshSize``
------------

**Type:** positive number. **Units:** metres. Sets the target Gmsh element size.

.. figure:: ../figs/mesh_1e4.png
   :alt: Mesh generated with size 1e-4 metres

.. figure:: ../figs/mesh_1e5.png
   :alt: Mesh generated with size 1e-5 metres

   Generated meshes with element sizes 1e-4 m and 1e-5 m.

Geometry modes
--------------

``image.mako`` sets the computational domain to the image extent.
``device.mako`` creates the micromodel geometry described by Benali (2019) and
Liu et al. (2023). Grain surfaces and device walls use no-slip conditions. The
templates can be modified for other element types or device geometries.

.. figure:: ../figs/device.png
   :alt: Geometry generated in device mode

   Geometry of the device mode.
