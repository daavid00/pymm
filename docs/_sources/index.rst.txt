pymm
====

An open-source image-based framework for computational fluid dynamics in microsystems.

.. grid:: 1 2 2 4
   :gutter: 2

   .. grid-item-card:: Get started
      :link: introduction
      :link-type: doc

      Learn what pymm does and how its image, mesh, flow, and tracer workflows connect.

   .. grid-item-card:: Install
      :link: installation
      :link-type: doc

      Install pymm, Gmsh, and OpenFOAM, then verify the external tools.

   .. grid-item-card:: Follow the tutorial
      :link: tutorial
      :link-type: doc

      Build a mesh, run flow and tracer simulations, and inspect the outputs.

   .. grid-item-card:: Explore examples
      :link: examples
      :link-type: doc

      Reproduce the image, device, and online-image cases.

Quick installation
------------------

.. code-block:: console

   pip install git+https://github.com/cssr-tools/pymm.git

Quick start
-----------

.. code-block:: console

   pymm -i microsystem.png -p parameters.toml -t all

What can pymm do?
-----------------

.. grid:: 1 2 2 3
   :gutter: 2

   .. grid-item-card:: Process images

      Segment grayscale microsystem images into grains and pore space.

   .. grid-item-card:: Generate meshes

      Extract polygonal boundaries and create three-dimensional Gmsh meshes.

   .. grid-item-card:: Simulate flow

      Run steady incompressible flow simulations with OpenFOAM.

   .. grid-item-card:: Transport tracers

      Run transient tracer-transport simulations and export VTK results.

   .. grid-item-card:: Build different domains

      Support image-sized and device-style computational domains.

.. toctree::
   :hidden:
   :maxdepth: 2

   introduction
   installation
   configuration_file
   tutorial
   examples
   command-line
   output_folder
   api
   contributing
   related
   