Introduction
============

.. image:: figs/pymm.gif
   :alt: Animated overview of the pymm workflow

**pymm** is an image-based framework for creating computational fluid-dynamics
models of microsystems. It uses `scikit-image <https://scikit-image.org>`_ to
segment images, `Gmsh <https://gmsh.info>`_ to generate meshes, and
`OpenFOAM <https://openfoam.org>`_ to simulate water flow and tracer transport.

Main workflows
--------------

* Process an image and generate diagnostic segmentation figures.
* Extract grain and external boundaries and generate a Gmsh mesh.
* Run a steady incompressible-flow simulation.
* Run a transient tracer-transport simulation from the flow field.

The current implementation supports general input images and two domain modes:
``image`` follows the image extent, while ``device`` adds the implemented
micromodel-device geometry. The templates can be extended for further devices
and OpenFOAM solvers.

Basic command
-------------

.. code-block:: console

   pymm -i image.png -p parameters.toml -o output -m image -t all -g gmsh

About the project
-----------------

pymm is an open-source project developed by NORCE Research AS. It is funded by
the Center for Sustainable Subsurface Resources, project 331841, and NORCE
Research AS, project 101070.

Citation
--------

If you use pymm in your research, please cite the archived software:

   Landa-Marbán, D. (2023). *pymm: An open-source image-based framework for CFD
   in microsystems*. Zenodo. https://doi.org/10.5281/zenodo.8430988

Where to continue
-----------------

* :doc:`installation` explains the Python, Gmsh, and OpenFOAM requirements.
* :doc:`configuration_file` documents every maintained TOML parameter.
* :doc:`tutorial` guides you through the complete workflow.
* :doc:`examples` collects reproducible image and device cases.
* :doc:`command-line` gives the parser-derived option and workflow reference.
* :doc:`output_folder` explains generated images, cases, meshes, and VTK data.
* :doc:`api` introduces the Python API and package layout.
